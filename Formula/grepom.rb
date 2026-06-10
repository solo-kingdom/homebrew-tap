class Grepom < Formula
  desc "Git Repository Orchestrator & Manager"
  homepage "https://github.com/sunzhenkai/grepom"
  url "https://github.com/sunzhenkai/grepom/archive/v0.1.3.tar.gz"
  version "0.1.3"
  sha256 "a6e01414ea0d6ef8321b9bf46a5b2be33ee3e7568510bfab17a419e3191dc341"
  license "MIT"
  head "https://github.com/sunzhenkai/grepom.git", branch: "master"

  depends_on "go" => :build

  def install
    ldflags = %W[
      -s -w
      -X main.version=#{version}
    ]
    system "go", "build", *std_go_args(ldflags:)
  end

  test do
    assert_match "grepom", shell_output("#{bin}/grepom --help")
  end
end
