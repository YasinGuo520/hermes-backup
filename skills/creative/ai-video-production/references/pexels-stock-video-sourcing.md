# Pexels Free Stock Video Sourcing for TikTok Videos

## How to find usable portrait videos

Search Pexels for portrait/vertical stock videos. Key search terms that work:

- `woman` + `portrait` + `lifestyle`
- `fashion` + `vertical video` (Pexels tags vertical as "Vertical Videos")
- `happy woman` + `smiling`
- `woman` + `clothes` + `shopping`
- `woman` + `thinking` + `expression`

Verified working videos from this session (all free, Pexels license):

| ID | Description | Resolution | Duration | Best for |
|----|-------------|-----------|----------|----------|
| 5585992 | Woman trying clothes by mirror | 1080×1920 @30fps | 4.2s | Hook / pain points |
| 8627840 | Happy woman smiling at camera | 1080×1920 @25fps | 8.6s | Product reveal / social proof |
| 6347113 | Woman shopping on smartphone | 2160×3840 @24fps | 10s | Features / CTA |
| 8627754 | Woman thinking/pondering | 1080×1920 @25fps | 12.8s | Problem setup / hook |

## Download pattern

### Direct CDN URL (works for some videos)
Pattern: `https://videos.pexels.com/video-files/{ID}/{ID}-hd_1080_1920_{fps}fps.mp4`
Some work, some return 403.

### Download redirect (works for ALL videos)
```bash
curl -sL -o video.mp4 "https://www.pexels.com/download/video/{ID}/" -H "User-Agent: Mozilla/5.0"
```
This follows the redirect to the real CDN URL.

## Processing pipeline

After downloading, process videos to match the composition:

1. **Downscale 4K to FHD**: `ffmpeg -i input.mp4 -vf "scale=1080:1920:flags=lanczos" -r 30 -c:v libx264 -preset fast -crf 23 output.mp4`
2. **Convert 25fps to 30fps**: `ffmpeg -i input.mp4 -r 30 -c:v libx264 -preset fast -crf 23 output.mp4`
3. **Cut segments**: `ffmpeg -i source.mp4 -t {secs} -c copy clip.mp4` or `ffmpeg -i source.mp4 -ss {start} -t {dur} -c copy clip.mp4`

## License note

Pexels videos are licensed under the Pexels License (free for commercial use, no attribution required). Always verify the license of specific videos before using in commercial content.
