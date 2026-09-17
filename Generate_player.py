import os
import html

# Define the extensions to look for
VIDEO_EXTENSIONS = ('.mp4', '.webm', '.ogg')

def generate_video_player():
    # Use the current directory where the script is running
    base_dir = os.getcwd()
    print(f"Scanning directory: {base_dir}")
    
    # HTML template with CSS for a split-screen layout
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Video Player</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            height: 100vh;
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        /* Sidebar layout */
        .sidebar {
            width: 300px;
            background-color: #262626;
            border-right: 1px solid #333;
            overflow-y: auto;
            padding: 15px;
        }
        .sidebar h2 {
            font-size: 1.2rem;
            margin-top: 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #444;
            color: #fff;
        }
        .folder-group {
            margin-bottom: 20px;
        }
        .folder-name {
            font-weight: bold;
            font-size: 0.95rem;
            margin-bottom: 8px;
            color: #4da6ff;
        }
        .video-list {
            list-style: none;
            padding-left: 10px;
            margin: 0;
        }
        .video-item {
            padding: 8px 10px;
            cursor: pointer;
            border-radius: 4px;
            font-size: 0.85rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 4px;
            background-color: #333;
            transition: background 0.2s;
        }
        .video-item:hover {
            background-color: #444;
        }
        .video-item.active {
            background-color: #007acc;
            color: #fff;
        }
        /* Main player layout */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            background-color: #111;
        }
        .video-container {
            width: 100%;
            max-width: 1000px;
            aspect-ratio: 16 / 9;
            background-color: #000;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            border-radius: 8px;
            overflow: hidden;
        }
        video {
            width: 100%;
            height: 100%;
        }
        .video-title {
            margin-top: 15px;
            font-size: 1.2rem;
            color: #fff;
            text-align: center;
        }
    </style>
</head>
<body>

    <div class="sidebar">
        <h2>Course Content</h2>
"""

    video_count = 0
    
    # Scan directories
    for root, dirs, files in os.walk(base_dir):
        video_files = sorted([f for f in files if f.lower().endswith(VIDEO_EXTENSIONS)])
        
        if video_files:
            video_count += len(video_files)
            rel_path = os.path.relpath(root, base_dir)
            folder_label = "Main Folder" if rel_path == "." else rel_path
            
            html_content += f'        <div class="folder-group">\n'
            html_content += f'            <div class="folder-name">{html.escape(folder_label)}</div>\n'
            html_content += f'            <ul class="video-list">\n'
            
            for video in video_files:
                video_rel_path = os.path.join(rel_path, video) if rel_path != "." else video
                web_path = video_rel_path.replace("\\", "/")
                
                # Get the name without the .mp4 extension safely
                clean_name = os.path.splitext(video)[0]
                
                html_content += f'                <li class="video-item" data-src="{html.escape(web_path)}" title="{html.escape(clean_name)}">{html.escape(clean_name)}</li>\n'
                
            html_content += f'            </ul>\n'
            html_content += f'        </div>\n'

    if video_count == 0:
        print("⚠️ Warning: No video files found in this folder or any subfolders!")
        html_content += '        <p style="color: #ff4d4d; font-size: 0.9rem;">No videos found. Make sure this script is placed in the correct course directory.</p>\n'
    else:
        print(f"✅ Found {video_count} videos.")

    # Add interactive JavaScript with LocalStorage tracking
    html_content += """    </div>

    <div class="main-content">
        <div class="video-container">
            <video id="videoPlayer" controls></video>
        </div>
        <div class="video-title" id="videoTitle">Select a video from the sidebar to begin</div>
    </div>

    <script>
        const player = document.getElementById('videoPlayer');
        const titleDisplay = document.getElementById('videoTitle');
        const items = document.querySelectorAll('.video-item');

        // Function to select and play a video
        function playVideo(item, savedTime = 0) {
            items.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            const src = item.getAttribute('data-src');
            const title = item.getAttribute('title');
            
            player.src = src;
            titleDisplay.textContent = title;
            
            // Save current video path to track last watched
            localStorage.setItem('lastWatchedVideo', src);
            
            // If we have a saved timestamp, apply it once metadata loads
            if (savedTime > 0) {
                player.addEventListener('loadedmetadata', function onMetadata() {
                    player.currentTime = savedTime;
                    player.removeEventListener('loadedmetadata', onMetadata);
                });
            }
            
            player.play().catch(err => console.log("Autoplay blocked or stream interrupted:", err));
        }

        // Click handler for sidebar links
        items.forEach(item => {
            item.addEventListener('click', function() {
                playVideo(this);
            });
        });

        // Continuously save progress (updates local storage every 2 seconds)
        player.addEventListener('timeupdate', () => {
            if (player.src) {
                localStorage.setItem('lastVideoTime', player.currentTime);
            }
        });

        // Auto-resume last video on page load
        window.addEventListener('DOMContentLoaded', () => {
            const lastVideo = localStorage.getItem('lastWatchedVideo');
            const lastTime = parseFloat(localStorage.getItem('lastVideoTime')) || 0;
            
            if (lastVideo) {
                // Find the sidebar item matching the saved source
                const savedItem = document.querySelector(`.video-item[data-src="${CSS.escape(lastVideo)}"]`);
                if (savedItem) {
                    // Load it back up with the saved time position
                    playVideo(savedItem, lastTime);
                }
            }
        });
    </script>
</body>
</html>
"""

    # Write out the script (Forces creation)
    output_file = os.path.join(base_dir, "player.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"📁 HTML file successfully created at: {output_file}")

if __name__ == "__main__":
    generate_video_player()
