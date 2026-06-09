class Transit < Formula
  include Language::Python::Virtualenv

  desc "Secure file transit service for multi-region network connectivity"
  homepage "https://github.com/solo-kingdom/transit"
  url "https://github.com/solo-kingdom/transit/archive/v0.1.1.tar.gz"
  version "0.1.1"
  sha256 "a6758e2306692cd88e1441dbddc9d64bd2c301c8aae4ea1d3c60035be618b499"
  license "Apache-2.0"
  head "https://github.com/solo-kingdom/transit.git", branch: "main"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources

    (bin/"transit-server").write_env_script(
      libexec/"bin/uvicorn",
      ["transit.main:app", "--host", "0.0.0.0", "--port", "9200"],
      {},
    )
  end

  test do
    assert_equal "ok", shell_output("#{libexec}/bin/python -c 'import transit; print(\"ok\")'").strip
  end
end
