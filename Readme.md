# GitHub Folder Downloader

A powerful Python utility that lets you download specific folders from GitHub repositories without cloning the entire repo.

![GitHub PGLoader Folder Downloader Banner](https://img.shields.io/badge/GitHub-PGLoader%20Folder%20Downloader-blue) ![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

<p align="center">
  <img src="GiTHuBSingleFolder.webp" alt="Centered Image" height=200px/>
</p>

## 🌟 Features

- **Selective downloading**: Download only the folders you need, not the entire repository
- **Progress tracking**: Real-time download and extraction progress bars
- **Robust error handling**: Automatic retries with exponential backoff for network issues
- **Path preservation**: Maintains the original folder structure
- **User-friendly**: Clear status updates and error messages
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Installation

```bash
# Clone this repository
git clone https://github.com/Priyanshu-i/PGLoader.git

# Navigate to the project directory
cd PGLoader

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

- Python 3.6+
- requests
- tqdm

## 📋 Usage

### Basic Usage

```bash
python PGLoader.py https://github.com/username/repo/tree/branch/folder
```

### Specify Output Directory

```bash
python PGLoader.py https://github.com/username/repo/tree/branch/folder -o custom_folder_name
```

### Increase Timeout for Slow Connections

```bash
python PGLoader.py https://github.com/username/repo/tree/branch/folder -t 120
```

### Force Overwrite Existing Directory

```bash
python PGLoader.py https://github.com/username/repo/tree/branch/folder -f
```

## 📊 Command Line Options

| Option | Description |
|--------|-------------|
| `url` | GitHub URL of the folder to download |
| `-o, --output` | Output directory name (default: folder name) |
| `-t, --timeout` | Connection timeout in seconds (default: 60) |
| `-r, --retries` | Number of retries for failed downloads (default: 3) |
| `-f, --force` | Force overwrite if output directory exists |

## 🔍 URL Format Examples

The tool accepts GitHub URLs in various formats:

- `https://github.com/username/repo/tree/branch/folder/path`
- `https://github.com/username/repo/tree/branch/folder`
- `https://github.com/username/repo` (downloads entire repo)

## 🛠️ How It Works

1. Parses the GitHub URL to extract the owner, repository, branch, and folder path
2. Downloads the repository as a zip archive
3. Extracts only the specified folder and its contents
4. Maintains the original folder structure

## 🧩 Examples

### Download a specific folder

```bash
python PGLoader.py https://github.com/geekan/MetaGPT/tree/main/metagpt
```

This downloads only the `metagpt` folder from the MetaGPT repository.

### Download with custom name

```bash
python PGLoader.py https://github.com/tensorflow/models/tree/master/official -o tf_official_models
```

This downloads the `official` folder from TensorFlow models repository and saves it as `tf_official_models`.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [GitHub API](https://docs.github.com/en/rest) for making this tool possible
- [requests](https://docs.python-requests.org/) library for HTTP requests
- [tqdm](https://github.com/tqdm/tqdm) library for progress bars

---

Made with ❤️ by Priyanshu Singh