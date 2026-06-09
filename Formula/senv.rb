class Senv < Formula
  desc "Secure environment variable and configuration manager"
  homepage "https://github.com/solo-kingdom/senv"
  url "https://github.com/solo-kingdom/senv/archive/v0.1.1.tar.gz"
  version "0.1.1"
  sha256 "29dd347e0eb549ae2716993ef8d6da87ecf2750affeba4a21dfed90bfb2e2d14"
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
