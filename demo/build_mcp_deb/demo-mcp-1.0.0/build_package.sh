set -x


rm -rf ../demo-mcp_1.0.0-1_all.deb ../demo-mcp_1.0.0-1_amd64.buildinfo ../demo-mcp_1.0.0-1_amd64.changes ../demo-mcp_1.0.0-1.dsc ../demo-mcp_1.0.0-1.tar.gz

dpkg-buildpackage -uc -us

dpkg -i --force-all ../demo-mcp_1.0.0-1_all.deb
