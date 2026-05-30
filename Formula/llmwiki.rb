class Llmwiki < Formula
  desc "Personal knowledge workspace"
  homepage "https://github.com/solo-kingdom/llmwiki"
  url "https://github.com/solo-kingdom/llmwiki/archive/2d2a350ed5cf75eb1c3639c9506b2b0c0421bded.tar.gz"
  version "0.1.0"
  sha256 "77459bde1999089558cf3684fa24efcc41096811dd7bcd8a5973174aa561c2a1"
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
      -X main.Commit=2d2a350
      -X main.BuildDate=#{time.iso8601}
    ]
    system "go", "build", *std_go_args(ldflags:), "./cmd/llmwiki/"
  end

  test do
    assert_match "structured wiki", shell_output("#{bin}/llmwiki --help")
  end
end
