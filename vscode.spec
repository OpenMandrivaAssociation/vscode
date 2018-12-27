Name:    vscode
Version: 1.30.1
Release: 1%{?dist}
Summary: Visual Studio Code - An open source code editor

Group:   Development/Tools
License: MIT
URL:     https://github.com/Microsoft/vscode
Source0: %{name}-master.tar.gz
Source1: https://github.com/Microsoft/vscode/archive/%{version}.tar.gz

BuildRequires: npm, node-gyp
BuildRequires: python, make, libX11-devel
BuildRequires: desktop-file-utils, git
Requires: electron

%description
 VS Code is a new type of tool that combines the simplicity of a code editor
 with what developers need for their core edit-build-debug cycle. Code provides
 comprehensive editing and debugging support, an extensibility model, and
 lightweight integration with existing tools.

%prep
%setup -q -n %{repo}-%{_commit}
sed -i '/electronVer/s|:.*,$|: "%{electron_ver}",|' package.json
git clone https://github.com/creationix/nvm.git .nvm
source .nvm/nvm.sh
nvm install %{node_ver}
nvm use %{node_ver}
npm config set python `which python`
npm install -g gulp

%build
export CFLAGS="%{optflags} -fPIC -pie"
export CXXFLAGS="%{optflags} -fPIC -pie"
source .nvm/nvm.sh
nvm use %{node_ver}
scripts/npm.sh install
gulp vscode-linux-%{arch}

%install
# Data files
mkdir --parents %{buildroot}%{_libdir}/%{name}
cp -a ../VSCode-linux-*/resources/app/. %{buildroot}%{_libdir}/%{name}

# Bin file
mkdir --parents %{buildroot}%{_bindir}
cat <<EOT >> %{buildroot}%{_bindir}/%{name}
#!/usr/bin/env bash
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.

NAME="%{name}"
VSCODE_PATH="%{_libdir}/\$NAME"
ELECTRON="%{_bindir}/electron"
CLI="\$VSCODE_PATH/out/cli.js"
ATOM_SHELL_INTERNAL_RUN_AS_NODE=1 "\$ELECTRON" "\$CLI" "\$@"
exit \$?
EOT

# Icon files
install -Dm 0644 resources/linux/code.png %{buildroot}%{_datadir}/pixmaps/%{name}.png

# Desktop file
mkdir --parents %{buildroot}%{_datadir}/applications
cat <<EOT >> %{buildroot}%{_datadir}/applications/%{name}.desktop
[Desktop Entry]
Type=Application
Name=Visual Studio Code
GenericName=VS Code
Comment=Code Editing. Redefined.
Exec=%{name}
Icon=%{name}
Terminal=false
Categories=GTK;Development;IDE;
MimeType=text/plain;text/x-chdr;text/x-csrc;text/x-c++hdr;text/x-c++src;text/x-java;text/x-dsrc;text/x-pascal;text/x-perl;text/x-python;application/x-php;application/x-httpd-php3;application/x-httpd-php4;application/x-httpd-php5;application/xml;text/html;text/css;text/x-sql;text/x-diff;
StartupNotify=true
EOT

desktop-file-install --mode 0644 %{buildroot}%{_datadir}/applications/%{name}.desktop

# Change appName
install -m 0644 %{S:1} %{buildroot}%{_libdir}/%{name}/product.json
sed -i -e \
   '/Short/s|:.*,$|: "VSCode",|
    /Long/s|:.*,$|: "Visual Studio Code",|' \
    %{buildroot}%{_libdir}/%{name}/product.json

# About.json
sed -i '$a\\t"commit": "%{_commit}",\n\t"date": "'`date -u +%FT%T.%3NZ`'"\n}' \
    %{buildroot}%{_libdir}/%{name}/product.json
sed -i '2s|:.*,$|: "VSCode",|' \
    %{buildroot}%{_libdir}/%{name}/package.json

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:
/usr/bin/update-desktop-database &>/dev/null ||:

%postun
if [ $1 -eq 0 ]; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null ||:
fi
/usr/bin/update-desktop-database &>/dev/null ||:

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null ||:

%files
%defattr(-,root,root,-)
%doc README.md ThirdPartyNotices.txt
%license LICENSE.txt
%{_bindir}/%{name}
%dir %{_libdir}/%{name}/
%{_libdir}/%{name}/*
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/applications/%{name}.desktop

%changelog
