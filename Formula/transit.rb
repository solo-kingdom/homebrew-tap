class Transit < Formula
  include Language::Python::Virtualenv

  desc "Secure file transit service for multi-region network connectivity"
  homepage "https://github.com/solo-kingdom/transit"
  url "https://github.com/solo-kingdom/transit/archive/1faf25a3a47c23c00c1d96d6bde48309363cff59.tar.gz"
  version "0.1.0"
  sha256 "dcf2206c6d5ca2785a59f0a9dce2175e859c7ef7d68542ca3d00c7e094570d8c"
  license "Apache-2.0"
  head "https://github.com/solo-kingdom/transit.git", branch: "main"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources

    (bin/"transit-server").write_env_script(
      libexec/"bin/uvicorn",
      "transit.main:app",
      "--host", "0.0.0.0",
      "--port", "9200"
    )
  end

  test do
    assert_match version.to_s, shell_output("#{libexec}/bin/python -c 'import transit; print(\"ok\")'")
  end
end
