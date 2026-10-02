#!/bin/bash

##############################################################################
# Design Tools Complete Setup
# Installs all dependencies for video, animation, and graphic design workflow
##############################################################################

set -e

echo "🎨 DESIGN TOOLS SETUP - Complete Installation"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS
OS_TYPE=$(uname -s)

##############################################################################
# 1. SYSTEM DEPENDENCIES
##############################################################################

echo -e "${BLUE}[1/5] Installing System Dependencies${NC}"

if [[ "$OS_TYPE" == "Linux" ]]; then
  echo "Detecting Linux distribution..."

  if command -v apt &> /dev/null; then
    # Debian/Ubuntu
    echo "Installing via apt (Debian/Ubuntu)..."
    sudo apt update
    sudo apt install -y \
      build-essential \
      curl \
      wget \
      git \
      python3 \
      python3-dev \
      python3-pip \
      ffmpeg \
      libssl-dev \
      libffi-dev \
      sox \
      libsox-dev \
      libsox-fmt-all
  elif command -v yum &> /dev/null; then
    # RedHat/CentOS/Fedora
    echo "Installing via yum (RedHat/CentOS)..."
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y \
      curl \
      wget \
      git \
      python3 \
      python3-devel \
      ffmpeg \
      openssl-devel \
      libffi-devel \
      sox \
      sox-devel
  fi

elif [[ "$OS_TYPE" == "Darwin" ]]; then
  # macOS
  echo "Installing via Homebrew (macOS)..."

  if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi

  brew install \
    curl \
    wget \
    git \
    python3 \
    ffmpeg \
    sox
fi

echo -e "${GREEN}✓ System dependencies installed${NC}"
echo ""

##############################################################################
# 2. NODE.JS (22+)
##############################################################################

echo -e "${BLUE}[2/5] Installing Node.js 22+${NC}"

if ! command -v node &> /dev/null; then
  echo "Node.js not found. Installing..."

  if [[ "$OS_TYPE" == "Darwin" ]]; then
    brew install node@22
    brew link node@22 --force
  else
    # Using NodeSource for Linux
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
  fi
else
  NODE_VERSION=$(node -v)
  echo "Node.js already installed: $NODE_VERSION"
fi

npm install -g npm@latest
echo -e "${GREEN}✓ Node.js 22+ installed${NC}"
echo ""

##############################################################################
# 3. PROJECT DEPENDENCIES
##############################################################################

echo -e "${BLUE}[3/5] Installing Project Dependencies${NC}"

cd "$(dirname "$0")"

# Install npm packages
if [ -f "package.json" ]; then
  echo "Installing npm packages..."
  npm install
else
  echo "Creating package.json..."
  npm init -y
  npm install --save \
    @remotion/cli \
    remotion \
    gsap \
    lottie-web \
    three \
    canvas \
    sharp \
    ffmpeg-static \
    ffprobe-static
fi

echo -e "${GREEN}✓ Project dependencies installed${NC}"
echo ""

##############################################################################
# 4. PYTHON ENVIRONMENT
##############################################################################

echo -e "${BLUE}[4/5] Setting up Python Environment${NC}"

# Create virtual environment
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
fi

# Activate venv
source venv/bin/activate || . venv/Scripts/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python packages
pip install -q \
  torch \
  transformers \
  scipy \
  numpy \
  pillow \
  opencv-python \
  manim \
  manim-ce \
  kokoro-onnx \
  soundfile \
  pydub \
  moviepy \
  imageio \
  imageio-ffmpeg

echo -e "${GREEN}✓ Python environment configured${NC}"
echo ""

##############################################################################
# 5. DIRECTORY STRUCTURE
##############################################################################

echo -e "${BLUE}[5/5] Creating Project Directories${NC}"

mkdir -p video
mkdir -p assets
mkdir -p renders
mkdir -p exports
mkdir -p vendor
mkdir -p scripts
mkdir -p .claude/skills
mkdir -p .claude/agents

echo -e "${GREEN}✓ Directory structure created${NC}"
echo ""

##############################################################################
# CONFIGURATION
##############################################################################

echo -e "${BLUE}Setting up Configuration${NC}"

# Create .env file if it doesn't exist
if [ ! -f "video/.env" ]; then
  echo "Creating video/.env..."
  cat > video/.env << 'EOF'
# HyperFrames Python (for Kokoro TTS)
HYPERFRAMES_PYTHON=python3

# Playwright Chromium path
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers

# API Keys (optional - for enhanced features)
# RUNWAYML_API_SECRET=your_secret_here
# FAL_KEY=your_key_here
# ELEVENLABS_API_KEY=your_key_here
# SUNO_API_KEY=your_key_here

# Video encoding
FFMPEG_CRF=14
FFMPEG_PRESET=slow
VIDEO_BITRATE=8000k
AUDIO_BITRATE=192k
EOF
  echo "Created video/.env - fill in API keys as needed"
fi

# Download GSAP if behind proxy
if [ ! -f "vendor/gsap.min.js" ]; then
  echo "Downloading GSAP (for local use)..."
  mkdir -p vendor
  curl -s https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js -o vendor/gsap.min.js
  echo "✓ GSAP downloaded"
fi

echo ""

##############################################################################
# VERIFICATION
##############################################################################

echo -e "${BLUE}Verifying Installation${NC}"
echo ""

# Check versions
echo "Version Information:"
echo "  Node: $(node -v)"
echo "  NPM: $(npm -v)"
echo "  Python: $(python3 --version)"
echo "  FFmpeg: $(ffmpeg -version | head -1)"
echo ""

# Check CLI tools
echo "Available CLIs:"
command -v remotion &> /dev/null && echo "  ✓ Remotion" || echo "  ✗ Remotion (install: npm install -g @remotion/cli)"
command -v manim &> /dev/null && echo "  ✓ Manim" || echo "  ✗ Manim"
command -v ffmpeg &> /dev/null && echo "  ✓ FFmpeg" || echo "  ✗ FFmpeg"
echo ""

##############################################################################
# COMPLETE
##############################################################################

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ DESIGN TOOLS SETUP COMPLETE${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure APIs (optional):"
echo "   nano video/.env"
echo ""
echo "2. Test the setup:"
echo "   npm run test:design"
echo ""
echo "3. Start creating content:"
echo "   npm run create:video"
echo ""
echo "4. Available skills:"
echo "   /animate - Motion design"
echo "   /hyperframes - Video rendering"
echo "   /impeccable - Visual design"
echo "   /manim-composer - Mathematical animation"
echo ""
echo "📚 Documentation: See PROYECTO_COMPLETO.md"
echo ""
