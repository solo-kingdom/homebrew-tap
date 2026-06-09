class Llmwiki < Formula
  desc "Personal knowledge workspace"
  homepage "https://github.com/solo-kingdom/llmwiki"
  url "https://github.com/solo-kingdom/llmwiki/archive/v0.1.1.tar.gz"
  version "0.1.1"
  sha256 "78f43272d49b2f7d4e14727ba1d09a81026548f6a34adc42389c0c519d071e18"
  license "MIT"
  head "https://github.com/solo-kingdom/llmwiki.git", branch: "main"

  depends_on "go" => :build
  depends_on "node" => :build

  def install
    cd "web" do
      system "npm", "install", *std_npm_args(prefix: false)
      system "npm", "run", "build"
    end

    ldflags = %W[
      -s -w
      -X main.Version=#{version}
      -X main.Commit=c443d56
      -X main.BuildDate=#{time.iso8601}
    ]
    system "go", "build", *std_go_args(ldflags:), "./cmd/llmwiki/"
  end

  test do
    assert_match "structured wiki", shell_output("#{bin}/llmwiki --help")
  end
end
