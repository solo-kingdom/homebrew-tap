class Grepom < Formula
  desc "Git Repository Orchestrator & Manager"
  homepage "https://github.com/sunzhenkai/grepom"
  url "https://github.com/sunzhenkai/grepom/archive/53278c6c4ed96a3070c83fccd72827f2d40300f8.tar.gz"
  version "0.1.0"
  sha256 "c66734f9d497091855899f38822e3eab810271c8be13652d5dcb0dc66a65ae35"
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
