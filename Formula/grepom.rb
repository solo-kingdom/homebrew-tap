class Grepom < Formula
  desc "Git Repository Orchestrator & Manager"
  homepage "https://github.com/sunzhenkai/grepom"
  url "https://github.com/sunzhenkai/grepom/archive/v0.1.4.tar.gz"
  version "0.1.4"
  sha256 "6a4c8f9d5064ec4f4f8e101955f80a1375dedf5ddbd87382c2517ca223783d5a"
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
