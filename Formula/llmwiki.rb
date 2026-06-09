class Llmwiki < Formula
  desc "Personal knowledge workspace"
  homepage "https://github.com/solo-kingdom/llmwiki"
  url "https://github.com/solo-kingdom/llmwiki/archive/c443d56bb68a9ebeff5bddccab783eb45078fbc0.tar.gz"
  version "0.1.0"
  sha256 "0dc39d3d3316a083aad110f4b208d4acbc9df40fdf47fca685e126614a4604e9"
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
