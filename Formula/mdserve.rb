class Mdserve < Formula
  desc "Real-time Markdown file server with web interface"
  homepage "https://github.com/sunzhenkai/mdserve"
  url "https://github.com/sunzhenkai/mdserve/archive/ce2bb79403c3566b145ad81e0da4e0258eb65d26.tar.gz"
  version "0.1.0"
  sha256 "1a6ffe6118140bce3064cc12ce92dedf11769ce0beda3ae1a4f3f12728f19f9f"
  license "MIT"
  head "https://github.com/sunzhenkai/mdserve.git", branch: "main"

  depends_on "go" => :build
  depends_on "node" => :build

  def install
    cd "web" do
      system "npm", "install", *std_npm_args(prefix: false)
      system "npm", "run", "build"
    end

    system "go", "build", *std_go_args, "./cmd/mdserve/"
  end

  test do
    assert_match "Markdown", shell_output("#{bin}/mdserve --help")
  end
end
