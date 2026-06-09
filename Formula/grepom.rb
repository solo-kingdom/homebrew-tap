class Grepom < Formula
  desc "Git Repository Orchestrator & Manager"
  homepage "https://github.com/sunzhenkai/grepom"
  url "https://github.com/sunzhenkai/grepom/archive/v0.1.2.tar.gz"
  version "0.1.2"
  sha256 "38bb041da3a1d1b3f4b8e40a6b810fa36786952e51ad0f6d8d8ab8fa6393f77e"
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
