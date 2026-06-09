class Mdserve < Formula
  desc "Real-time Markdown file server with web interface"
  homepage "https://github.com/sunzhenkai/mdserve"
  url "https://github.com/sunzhenkai/mdserve/archive/v0.1.1.tar.gz"
  version "0.1.1"
  sha256 "befd4a7df6c9a53449a35670211c634993af9224611253ea81c8c6226c729857"
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
