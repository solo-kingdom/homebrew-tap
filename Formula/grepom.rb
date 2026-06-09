class Grepom < Formula
  desc "Git Repository Orchestrator & Manager"
  homepage "https://github.com/sunzhenkai/grepom"
  url "https://github.com/sunzhenkai/grepom/archive/eb367d6193eb4da30bdc1a627eed70cf304e781f.tar.gz"
  version "0.1.0"
  sha256 "a097b4bc44f7740206de738948d434d65fcf790a5907590f6893f2610787e09d"
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
