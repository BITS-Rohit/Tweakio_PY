import os
import json
import subprocess
import requests
from urllib.parse import quote_plus
from pathlib import Path
from dateutil import parser as dateparser


class YoutubeAPI:
    BASE_URL = "https://www.googleapis.com/youtube/v3/search?part=snippet&q="
    MAX_RESULTS = 10
    YT_DLP_PATH = "/usr/local/bin/yt-dlp"

    def __init__(self, API_KEY):
        self.api_key = API_KEY
        self.session = requests.Session()

    # -----------------------------------------------------------
    # YOUTUBE SEARCH
    # -----------------------------------------------------------

    def search(self, query: str) -> str:
        print(f"🛠️ Received query: {query}")

        encoded = quote_plus(query)
        url = (
            f"{self.BASE_URL}{encoded}"
            f"&key={self.api_key}"
            f"&type=video"
            f"&maxResults={self.MAX_RESULTS}"
        )

        print("🛠️ Calling URL:", url)

        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

        except Exception as e:
            return f"⚠️ Network/API error: {e}"

        # API error
        if "error" in data:
            msg = data["error"].get("message", "Unknown error")
            return f"⚠️ YouTube API error: {msg}"

        items = data.get("items", [])
        if not items:
            return f"⚠️ No results found for \"{query}\"."

        video_ids = [item["id"]["videoId"] for item in items if "videoId" in item["id"]]
        if not video_ids:
            return f"⚠️ No videos found in search results."

        # Get details
        return self._fetch_details(",".join(video_ids), items)

    # -----------------------------------------------------------
    # VIDEO DETAILS
    # -----------------------------------------------------------

    def _fetch_details(self, video_ids, first_call_items):
        url = (
            "https://www.googleapis.com/youtube/v3/videos"
            f"?part=snippet,statistics,contentDetails&id={video_ids}&key={self.api_key}"
        )
        resp = self.session.get(url, timeout=10)
        data = resp.json()

        items = data.get("items", [])
        if not items:
            return "⚠️ Failed to fetch video details."

        response_text = []

        for i, video in enumerate(items):
            snippet = video.get("snippet", {})
            content = video.get("contentDetails", {})
            stats = video.get("statistics", {})
            base_snippet = first_call_items[i]["snippet"]

            # Fields
            title = snippet.get("title", "N/A")
            video_id = video.get("id", "N/A")
            channel = snippet.get("channelTitle", "Unknown Channel")
            description = base_snippet.get("description", "No description.")
            dur = self._format_duration(content.get("duration"))
            quality = content.get("definition", "N/A")
            licensed = str(content.get("licensedContent", False))
            views = stats.get("viewCount", "N/A")
            likes = stats.get("likeCount", "N/A")
            comments = stats.get("commentCount", "N/A")
            publish_time = self._format_date(snippet.get("publishedAt"))
            thumbnail = self._choose_thumbnail(snippet.get("thumbnails", {}))

            block = (
                f"🎥 Title: {title}\n"
                f"📺 Channel: {channel}\n"
                f"🗓️ Published: {publish_time}\n"
                f"📝 Description: {description}\n"
                f"📹 Video ID: {video_id}\n"
                f"🔗 Link: https://www.youtube.com/watch?v={video_id}\n"
                f"🖼️ Thumbnail: {thumbnail}\n"
                f"⏱️ Duration: {dur}\n"
                f"📽️ Quality: {quality}\n"
                f"🔐 Licensed: {licensed}\n"
                f"👁️ Views: {views}\n"
                f"👍 Likes: {likes}\n"
                f"💬 Comments: {comments}\n"
                "---------------------------------------------------\n"
            )

            response_text.append(block)

        return "".join(response_text)

    # -----------------------------------------------------------
    # UTILITIES
    # -----------------------------------------------------------

    def _choose_thumbnail(self, thumbs):
        for key in ["maxres", "high", "default"]:
            if key in thumbs:
                return thumbs[key]["url"]
        return "No thumbnail available."

    def _format_duration(self, iso):
        if not iso:
            return "N/A"

        # Example: PT1H2M5S
        import isodate
        try:
            d = isodate.parse_duration(iso)
        except:
            return iso

        total_seconds = int(d.total_seconds())
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60

        if h:
            return f"{h}h {m}m {s}s"
        if m:
            return f"{m}m {s}s"
        return f"{s}s"

    def _format_date(self, iso):
        try:
            dt = dateparser.parse(iso)
            return dt.strftime("%d %b %Y")
        except:
            return iso or "N/A"

    # -----------------------------------------------------------
    # YT-DLP MP3 DOWNLOAD
    # -----------------------------------------------------------
    def clean_url(self, url: str) -> str:
        url.strip()
        # Keep only the last valid URL
        parts = url.split()
        for part in reversed(parts):
            if part.startswith("http://") or part.startswith("https://"):
                return part
        return url

    def download_audio(self, link: str):
        """ Returns the file path for downloaded audio"""
        save_dir = Path(os.getcwd()) / "FilesSaved"
        save_dir.mkdir(exist_ok=True)

        output_template = str(save_dir / "%(title)s.%(ext)s")

        cleaned = self.clean_url(url=link)

        cmd = [
            self.YT_DLP_PATH, "-f", "bestaudio", "-x",
            "--audio-format", "mp3",
            "--restrict-filenames",
            "-o", output_template,
            cleaned
        ]

        print("Running yt-dlp:", " ".join(cmd))

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            final_file = None

            for line in proc.stdout:
                line = line.strip()
                print(line)

                if "Destination:" in line:
                    final_file = line.split("Destination:")[-1].strip()

            proc.wait()

            if proc.returncode == 0 and final_file:
                final_path = Path(final_file)
                if final_path.exists():
                    return str(final_path)

            return "❌ Download failed or file not found."

        except Exception as e:
            return f"❌ Error: {e}"

    # -----------------------------------------------------------
    # YT-DLP SEARCH
    # -----------------------------------------------------------

    def ytdlp_search(self, query="Nvidia", count=5):
        """YT dlp internal search module"""
        search = f"ytsearch{count}:{query}"
        cmd = [self.YT_DLP_PATH, "-j", search]

        results = []
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in proc.stdout:
                line = line.strip()
                if line.startswith("{"):
                    try:
                        results.append(json.loads(line))
                    except:
                        print("⚠️ Invalid JSON:", line)

            proc.wait()

        except Exception as e:
            print("❌ Error executing yt-dlp:", e)
            return

        for video in results:
            print("🎬 Title:", video.get("title", "No Title"))
            print("🔗 URL:", video.get("webpage_url", "No URL"))
            print("🖼️ Thumb:", video.get("thumbnail", "No Thumbnail"))
            print("------------")

def main():
    yt = YoutubeAPI(API_KEY=API_KEY)

    print("\n===== 🔍 YOUTUBE SEARCH TEST =====")
    result = yt.search("Nvidia GPU review")
    print(result)

    print("\n===== 🎵 YT-DLP AUDIO DOWNLOAD TEST =====")
    audio_file = yt.download_audio("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print("Downloaded file:", audio_file)

    print("\n===== 🎥 YT-DLP SEARCH TEST =====")
    yt.ytdlp_search("Python automation", count=3)


if __name__ == "__main__":
    main()