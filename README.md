# FFmpeg Installation Guide for Pythonese Translator

Your application requires FFmpeg to handle audio conversion. The error you're seeing indicates that FFmpeg is not installed or not found in your system path. Here's how to install it:

## Windows Installation

1. **Download FFmpeg**:
   - Go to [FFmpeg.org](https://ffmpeg.org/download.html) or [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) for Windows builds
   - Download the "essentials" or "full" build (the 7z or zip archive)

2. **Extract FFmpeg**:
   - Extract the downloaded archive to a location like `C:\ffmpeg`
   - The bin folder should contain files like `ffmpeg.exe`, `ffprobe.exe`, etc.

3. **Add FFmpeg to PATH**:
   - Right-click on "This PC" or "My Computer" and select "Properties"
   - Click on "Advanced system settings"
   - Click the "Environment Variables" button
   - Under "System variables", find the "Path" variable and click "Edit"
   - Click "New" and add the path to the bin folder (e.g., `C:\ffmpeg\bin`)
   - Click "OK" on all dialogs to save

    3a. **Quick Alternative Setup**:
      - Alternatively, extract the FFmpeg files to a new folder named `ffmpeg` inside your application directory
      - The code will automatically check this location

4. **Verify Installation**:
   - Open a new command prompt window (important to refresh environment variables)
   - Type `ffmpeg -version` and press Enter
   - If successful, you should see version information

## Mac Installation

Using Homebrew:
```bash
brew install ffmpeg
```

## Linux Installation

Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

Fedora:
```bash
sudo dnf install ffmpeg
```

## Testing After Installation

After installing FFmpeg, restart your Flask application and try the speech recording feature again. The error should be resolved.

If you continue to have issues, ensure that:
1. The FFmpeg binaries are properly installed
2. The path to FFmpeg is correctly set in your environment variables
3. You've restarted your application server after making these changes


# Running the Application
To run the application, follow these steps:
1. Install the required packages using `pip install -r requirements.txt`.
   - If you encounter issues with `ffmpeg`, ensure you have FFmpeg installed and its path is correctly set in your environment variables.
   - If you're using a virtual environment, activate it before installing packages.

2. Run the application using `python app.py`.
   - If you're using a virtual environment, activate it before running the application.
   - If you're using a different port, update the `app.run()` call in `app.py` to use the desired port.

3. Access the application in your web browser at `http://localhost:5000`, or `http://127.0.0.1:5000`.
   - If you're using a different port, replace `5000` with the port you've specified in `app.py`.