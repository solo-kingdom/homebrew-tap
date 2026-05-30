class Senv < Formula
  desc "Secure environment variable and configuration manager"
  homepage "https://github.com/solo-kingdom/senv"
  url "https://github.com/solo-kingdom/senv/archive/f67242ce56d77e2014c678c1c5bfd2189f00c06c.tar.gz"
  version "0.1.0"
  sha256 "486fd97bbc67c294b976750bd072fff4a1e06ab34212bdc50a2ffc8c59076890"
  license "MIT"
  head "https://github.com/solo-kingdom/senv.git", branch: "main"

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args, "./main.go"
  end

  test do
    assert_match "environment variables", shell_output("#{bin}/senv --help")
  end
end
