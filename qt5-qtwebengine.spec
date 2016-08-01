
%global qt_module qtwebengine

%global _hardened_build 1

# define to build docs, need to undef this for bootstrapping
# where qt5-qttools builds are not yet available
# only primary archs (for now), allow secondary to bootstrap
%ifarch %{arm} %{ix86} x86_64
%global docs 1
%endif

%if 0%{?fedora} > 22
# need libvpx >= 1.4.0
%global use_system_libvpx 1
%endif
%if 0%{?fedora} || 0%{?rhel} > 6
# need libwebp >= 0.4.3
%global use_system_libwebp 1
%endif

#global prerelease rc

# exclude plugins (all architectures) and libv8.so (i686, it's static everywhere
# else)
%global __provides_exclude ^lib.*plugin\\.so.*|libv8\\.so$
# exclude libv8.so (i686, it's static everywhere else)
%global __requires_exclude ^libv8\\.so$

Summary: Qt5 - QtWebEngine components
Name:    qt5-qtwebengine
Version: 5.6.1
Release: 4%{?dist}

# See LICENSE.GPL LICENSE.LGPL LGPL_EXCEPTION.txt, for details
# See also http://qt-project.org/doc/qt-5.0/qtdoc/licensing.html
# The other licenses are from Chromium and the code it bundles
License: (LGPLv2 with exceptions or GPLv3 with exceptions) and BSD and LGPLv2+ and ASL 2.0 and IJG and MIT and GPLv2+ and ISC and OpenSSL and (MPLv1.1 or GPLv2 or LGPLv2)
URL:     http://www.qt.io
# cleaned tarball with patent-encumbered codecs removed from the bundled FFmpeg
# wget http://download.qt.io/official_releases/qt/5.6/5.6.1/submodules/qtwebengine-opensource-src-5.6.1.tar.xz
# ./clean_qtwebengine.sh 5.6.1
Source0: qtwebengine-opensource-src-%{version}-clean.tar.xz
# cleanup scripts used above
Source1: clean_qtwebengine.sh
Source2: clean_ffmpeg.sh
Source3: process_ffmpeg_gyp.py
# do not compile with -Wno-format, which also bypasses -Werror-format-security
Patch0:  qtwebengine-opensource-src-5.6.0-beta-no-format.patch
# some tweaks to linux.pri (system libs, link libpci, run unbundling script)
Patch1:  qtwebengine-opensource-src-5.6.1-linux-pri.patch
# quick hack to avoid checking for the nonexistent icudtl.dat and silence the
# resulting warnings - not upstreamable as is because it removes the fallback
# mechanism for the ICU data directory (which is not used in our builds because
# we use the system ICU, which embeds the data statically) completely
Patch2:  qtwebengine-opensource-src-5.6.0-no-icudtl-dat.patch
# fix extractCFlag to also look in QMAKE_CFLAGS_RELEASE, needed to detect the
# ARM flags with our %%qmake_qt5 macro, including for the next patch
Patch3:  qtwebengine-opensource-src-5.6.0-beta-fix-extractcflag.patch
# disable NEON vector instructions on ARM for now, the NEON code FTBFS due to
# GCC bug https://bugzilla.redhat.com/show_bug.cgi?id=1282495
Patch4:  qtwebengine-opensource-src-5.6.0-beta-no-neon.patch
# use the system NSPR prtime (based on Debian patch)
# We already depend on NSPR, so it is useless to copy these functions here.
# Debian uses this just fine, and I don't see relevant modifications either.
Patch5:  qtwebengine-opensource-src-5.6.0-beta-system-nspr-prtime.patch
# use the system ICU UTF functions
# We already depend on ICU, so it is useless to copy these functions here.
# I checked the history of that directory, and other than the renames I am
# undoing, there were no modifications at all. Must be applied after Patch5.
Patch6:  qtwebengine-opensource-src-5.6.0-beta-system-icu-utf.patch
# do not require SSE2 on i686
# cumulative revert of upstream reviews 187423002, 308003004, 511773002 (parts
# relevant to QtWebEngine only), 516543004, 1152053004 and 1161853008, along
# with some custom fixes and improvements
# also build V8 shared and twice on i686 (once for x87, once for SSE2)
Patch7:  qtwebengine-opensource-src-5.6.1-no-sse2.patch

# the architectures theoretically supported by the version of V8 used (#1298011)
# You may need some minor patching to build on one of the secondary
# architectures, e.g., to add to the Qt -> Chromium -> V8 arch translations.
# If you cannot get this package to build on your secondary architecure, please:
# * remove your architecture from this list AND
# * put #1298011 onto your ExcludeArch tracker.
ExclusiveArch: %{ix86} x86_64 %{arm} aarch64 mips mipsel mips64el

BuildRequires: qt5-qtbase-devel >= %{version}
BuildRequires: qt5-qtbase-private-devel
# TODO: check of = is really needed or if >= would be good enough -- rex
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}
BuildRequires: qt5-qtdeclarative-devel >= %{version}
BuildRequires: qt5-qtxmlpatterns-devel >= %{version}
BuildRequires: qt5-qtlocation-devel >= %{version}
BuildRequires: qt5-qtsensors-devel >= %{version}
BuildRequires: qt5-qtwebchannel-devel >= %{version}
BuildRequires: qt5-qttools-static >= %{version}
BuildRequires: ninja-build
BuildRequires: cmake
BuildRequires: bison
BuildRequires: git-core
BuildRequires: gperf
BuildRequires: libicu-devel
BuildRequires: libjpeg-devel
BuildRequires: re2-devel
BuildRequires: snappy-devel
%ifarch %{ix86} x86_64
BuildRequires: yasm
%endif
BuildRequires: pkgconfig(expat)
BuildRequires: pkgconfig(gobject-2.0)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(fontconfig)
BuildRequires: pkgconfig(freetype2)
BuildRequires: pkgconfig(gl)
BuildRequires: pkgconfig(egl)
BuildRequires: pkgconfig(libpng)
BuildRequires: pkgconfig(libudev)
%if 0%{?use_system_libwebp}
BuildRequires: pkgconfig(libwebp) >= 0.4.3
%endif
BuildRequires: pkgconfig(harfbuzz)
BuildRequires: pkgconfig(jsoncpp)
BuildRequires: pkgconfig(protobuf)
BuildRequires: pkgconfig(libdrm)
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(libevent)
BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(minizip)
BuildRequires: pkgconfig(libxml-2.0)
BuildRequires: pkgconfig(libxslt)
BuildRequires: pkgconfig(x11)
BuildRequires: pkgconfig(xi)
BuildRequires: pkgconfig(xcursor)
BuildRequires: pkgconfig(xext)
BuildRequires: pkgconfig(xfixes)
BuildRequires: pkgconfig(xrender)
BuildRequires: pkgconfig(xdamage)
BuildRequires: pkgconfig(xcomposite)
BuildRequires: pkgconfig(xtst)
BuildRequires: pkgconfig(xrandr)
BuildRequires: pkgconfig(xscrnsaver)
BuildRequires: pkgconfig(libcap)
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(alsa)
BuildRequires: pkgconfig(libpci)
BuildRequires: pkgconfig(dbus-1)
BuildRequires: pkgconfig(nss)
BuildRequires: pkgconfig(libsrtp)
BuildRequires: perl
BuildRequires: python
%if 0%{?use_system_libvpx}
BuildRequires: pkgconfig(vpx) >= 1.4.0
%endif

# extra (non-upstream) functions needed, see
# src/3rdparty/chromium/third_party/sqlite/README.chromium for details
#BuildRequires: pkgconfig(sqlite3)

## Various bundled libraries that Chromium does not support unbundling :-(
## Only the parts actually built are listed.
## Query for candidates:
## grep third_party/ build.log | sed 's!third_party/!\nthird_party/!g' | \
## grep third_party/ | sed 's!^third_party/!!g' | sed 's!/.*$!!g' | \
## sed 's/\;.*$//g' | sed 's/ .*$//g' | sort | uniq | less
## some false positives where only shim headers are generated for some reason
## some false positives with dummy placeholder dirs (swiftshader, widevine)
## some false negatives where a header-only library is bundled (e.g. x86inc)
## Spot's chromium.spec also has a list that I checked.

# Of course, Chromium itself is bundled. It cannot be unbundled because it is
# not a library, but forked (modified) application code.
# Some security fixes are backported, see:
# http://code.qt.io/cgit/qt/qtwebengine-chromium.git/log/?h=45-based
Provides: bundled(chromium) = 45

# Bundled in src/3rdparty/chromium/third_party:
# Check src/3rdparty/chromium/third_party/*/README.chromium for version numbers,
# except where specified otherwise.
Provides: bundled(angle) = 2422
# Google's fork of OpenSSL
# We cannot build against NSS instead because it no longer works with NSS 3.21:
# HTTPS on, ironically, Google's sites (Google, YouTube, etc.) stops working
# completely and produces only ERR_SSL_PROTOCOL_ERROR errors:
# http://kaosx.us/phpBB3/viewtopic.php?t=1235
# https://bugs.launchpad.net/ubuntu/+source/chromium-browser/+bug/1520568
# So we have to do what Chromium 47 now defaults to: a "chimera build", i.e.,
# use the BoringSSL code and the system NSS certificates.
Provides: bundled(boringssl)
Provides: bundled(brotli)
# Don't get too excited. MPEG and other legally problematic stuff is stripped
# out. See clean_qtwebengine.sh, clean_ffmpeg.sh, and process_ffmpeg_gyp.py.
# see src/3rdparty/chromium/third_party/ffmpeg/Changelog for the version number
Provides: bundled(ffmpeg) = 2.7
Provides: bundled(iccjpeg)
# bundled as "khronos", headers only
Provides: bundled(khronos_headers)
# bundled as "leveldatabase"
Provides: bundled(leveldb) = r80
Provides: bundled(libjingle) = 9564
%if !0%{?use_system_libvpx}
Provides: bundled(libvpx) = 1.4.0
%endif
%if !0%{?use_system_libwebp}
Provides: bundled(libwebp) = 0.4.3
%endif
Provides: bundled(libXNVCtrl) = 302.17
Provides: bundled(libyuv) = 1444
Provides: bundled(modp_b64)
Provides: bundled(mojo)
# headers only
Provides: bundled(npapi)
Provides: bundled(openmax_dl) = 1.0.2
Provides: bundled(ots)
Provides: bundled(qcms) = 4
Provides: bundled(sfntly) = 0-0.1.svn111
Provides: bundled(skia)
# bundled as "smhasher"
Provides: bundled(SMHasher) = 0-0.1.svn147
Provides: bundled(sqlite) = 3.8.7.4
Provides: bundled(usrsctp) = 0-0.1.svn9045
Provides: bundled(webrtc) = 90
%ifarch %{ix86} x86_64
# header (for assembly) only
Provides: bundled(x86inc) = 0
%endif

# Bundled in src/3rdparty/chromium/base/third_party:
# Check src/3rdparty/chromium/third_party/base/*/README.chromium for version
# numbers, except where specified otherwise.
Provides: bundled(dmg_fp)
Provides: bundled(dynamic_annotations) = 4384
Provides: bundled(superfasthash) = 0
Provides: bundled(symbolize)
# bundled as "valgrind", headers only
Provides: bundled(valgrind.h)
# bundled as "xdg_mime"
Provides: bundled(xdg-mime)
# bundled as "xdg_user_dirs"
Provides: bundled(xdg-user-dirs) = 0.10

# Bundled in src/3rdparty/chromium/net/third_party:
# Check src/3rdparty/chromium/third_party/net/*/README.chromium for version
# numbers, except where specified otherwise.
Provides: bundled(mozilla_security_manager) = 1.9.2

# Bundled in src/3rdparty/chromium/url/third_party:
# Check src/3rdparty/chromium/third_party/url/*/README.chromium for version
# numbers, except where specified otherwise.
# bundled as "mozilla", file renamed and modified
Provides: bundled(nsURLParsers)

# Bundled outside of third_party, apparently not considered as such by Chromium:
# see src/3rdparty/chromium/v8/include/v8_version.h for the version number
Provides: bundled(v8) = 4.5.103.35
# bundled by v8 (src/3rdparty/chromium/v8/src/third_party/fdlibm)
# see src/3rdparty/chromium/v8/src/third_party/fdlibm/README.v8 for the version
Provides: bundled(fdlibm) = 5.3

%{?_qt5_version:Requires: qt5-qtbase%{?_isa} >= %{_qt5_version}}


%description
%{summary}.

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: qt5-qtbase-devel%{?_isa}
Requires: qt5-qtdeclarative-devel%{?_isa}
%description devel
%{summary}.

%package examples
Summary: Example files for %{name}

%description examples
%{summary}.


%if 0%{?docs}
%package doc
Summary: API documentation for %{name}
BuildRequires: qt5-qhelpgenerator
BuildRequires: qt5-qdoc
BuildArch: noarch
%description doc
%{summary}.
%endif


%prep
%setup -q -n %{qt_module}-opensource-src-%{version}%{?prerelease:-%{prerelease}}
%patch0 -p1 -b .no-format
%patch1 -p1 -b .linux-pri
%patch2 -p1 -b .no-icudtl-dat
%patch3 -p1 -b .fix-extractcflag
%patch4 -p1 -b .no-neon
%patch5 -p1 -b .system-nspr-prtime
%patch6 -p1 -b .system-icu-utf
%patch7 -p1 -b .no-sse2
# fix // in #include in content/renderer/gpu to avoid debugedit failure
sed -i -e 's!gpu//!gpu/!g' \
  src/3rdparty/chromium/content/renderer/gpu/compositor_forwarding_message_filter.cc
# remove ./ from #line commands in ANGLE to avoid debugedit failure (?)
sed -i -e 's!\./!!g' \
  src/3rdparty/chromium/third_party/angle/src/compiler/preprocessor/Tokenizer.cpp \
  src/3rdparty/chromium/third_party/angle/src/compiler/translator/glslang_lex.cpp

# http://bugzilla.redhat.com/1337585
# can't just delete, but we'll overwrite with system headers to be on the safe side
cp -bv /usr/include/re2/*.h src/3rdparty/chromium/third_party/re2/re2/

%ifnarch x86_64
# most arches run out of memory with full debuginfo, so use -g1 on non-x86_64
sed -i -e 's/=-g$/=-g1/g' src/core/gyp_run.pro
%endif

%build
export STRIP=strip
export NINJAFLAGS="-v %{_smp_mflags}"
export NINJA_PATH=%{_bindir}/ninja-build
export CXXFLAGS="%{optflags} -fno-delete-null-pointer-checks"
%ifnarch x86_64
# most arches run out of memory with full debuginfo, so use -g1 on non-x86_64
export CXXFLAGS=`echo "$CXXFLAGS" | sed -e 's/ -g / -g1 /g'`
%endif

mkdir %{_target_platform}
pushd %{_target_platform}

%{qmake_qt5} CONFIG+="webcore_debug v8base_debug force_debug_info" WEBENGINE_CONFIG+="use_system_icu" ..

# workaround, disable parallel compilation as it fails to compile in brew
make %{?_smp_mflags}

%if 0%{?docs}
make %{?_smp_mflags} docs
%endif
popd

%install
make install INSTALL_ROOT=%{buildroot} -C %{_target_platform}

%if 0%{?docs}
make install_docs INSTALL_ROOT=%{buildroot} -C %{_target_platform}
%endif

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%{_qt5_libdir}/libQt5*.so.*
%{_qt5_libdir}/qt5/qml/*
%{_qt5_libdir}/qt5/libexec/QtWebEngineProcess
%ifarch %{ix86}
# shared V8 library and its SSE2 version
%{_qt5_libdir}/qtwebengine/
%endif
%{_qt5_plugindir}/designer/libqwebengineview.so
%{_qt5_datadir}/resources/
%dir %{_qt5_translationdir}/qtwebengine_locales
%lang(am) %{_qt5_translationdir}/qtwebengine_locales/am.pak
%lang(ar) %{_qt5_translationdir}/qtwebengine_locales/ar.pak
%lang(bg) %{_qt5_translationdir}/qtwebengine_locales/bg.pak
%lang(bn) %{_qt5_translationdir}/qtwebengine_locales/bn.pak
%lang(ca) %{_qt5_translationdir}/qtwebengine_locales/ca.pak
%lang(cs) %{_qt5_translationdir}/qtwebengine_locales/cs.pak
%lang(da) %{_qt5_translationdir}/qtwebengine_locales/da.pak
%lang(de) %{_qt5_translationdir}/qtwebengine_locales/de.pak
%lang(el) %{_qt5_translationdir}/qtwebengine_locales/el.pak
%lang(en) %{_qt5_translationdir}/qtwebengine_locales/en-GB.pak
%lang(en) %{_qt5_translationdir}/qtwebengine_locales/en-US.pak
%lang(es) %{_qt5_translationdir}/qtwebengine_locales/es-419.pak
%lang(es) %{_qt5_translationdir}/qtwebengine_locales/es.pak
%lang(et) %{_qt5_translationdir}/qtwebengine_locales/et.pak
%lang(fa) %{_qt5_translationdir}/qtwebengine_locales/fa.pak
%lang(fi) %{_qt5_translationdir}/qtwebengine_locales/fi.pak
%lang(fil) %{_qt5_translationdir}/qtwebengine_locales/fil.pak
%lang(fr) %{_qt5_translationdir}/qtwebengine_locales/fr.pak
%lang(gu) %{_qt5_translationdir}/qtwebengine_locales/gu.pak
%lang(he) %{_qt5_translationdir}/qtwebengine_locales/he.pak
%lang(hi) %{_qt5_translationdir}/qtwebengine_locales/hi.pak
%lang(hr) %{_qt5_translationdir}/qtwebengine_locales/hr.pak
%lang(hu) %{_qt5_translationdir}/qtwebengine_locales/hu.pak
%lang(id) %{_qt5_translationdir}/qtwebengine_locales/id.pak
%lang(it) %{_qt5_translationdir}/qtwebengine_locales/it.pak
%lang(ja) %{_qt5_translationdir}/qtwebengine_locales/ja.pak
%lang(kn) %{_qt5_translationdir}/qtwebengine_locales/kn.pak
%lang(ko) %{_qt5_translationdir}/qtwebengine_locales/ko.pak
%lang(lt) %{_qt5_translationdir}/qtwebengine_locales/lt.pak
%lang(lv) %{_qt5_translationdir}/qtwebengine_locales/lv.pak
%lang(ml) %{_qt5_translationdir}/qtwebengine_locales/ml.pak
%lang(mr) %{_qt5_translationdir}/qtwebengine_locales/mr.pak
%lang(ms) %{_qt5_translationdir}/qtwebengine_locales/ms.pak
%lang(nb) %{_qt5_translationdir}/qtwebengine_locales/nb.pak
%lang(nl) %{_qt5_translationdir}/qtwebengine_locales/nl.pak
%lang(pl) %{_qt5_translationdir}/qtwebengine_locales/pl.pak
%lang(pt_BR) %{_qt5_translationdir}/qtwebengine_locales/pt-BR.pak
%lang(pt_PT) %{_qt5_translationdir}/qtwebengine_locales/pt-PT.pak
%lang(ro) %{_qt5_translationdir}/qtwebengine_locales/ro.pak
%lang(ru) %{_qt5_translationdir}/qtwebengine_locales/ru.pak
%lang(sk) %{_qt5_translationdir}/qtwebengine_locales/sk.pak
%lang(sl) %{_qt5_translationdir}/qtwebengine_locales/sl.pak
%lang(sr) %{_qt5_translationdir}/qtwebengine_locales/sr.pak
%lang(sv) %{_qt5_translationdir}/qtwebengine_locales/sv.pak
%lang(sw) %{_qt5_translationdir}/qtwebengine_locales/sw.pak
%lang(ta) %{_qt5_translationdir}/qtwebengine_locales/ta.pak
%lang(te) %{_qt5_translationdir}/qtwebengine_locales/te.pak
%lang(th) %{_qt5_translationdir}/qtwebengine_locales/th.pak
%lang(tr) %{_qt5_translationdir}/qtwebengine_locales/tr.pak
%lang(uk) %{_qt5_translationdir}/qtwebengine_locales/uk.pak
%lang(vi) %{_qt5_translationdir}/qtwebengine_locales/vi.pak
%lang(zh_CN) %{_qt5_translationdir}/qtwebengine_locales/zh-CN.pak
%lang(zh_TW) %{_qt5_translationdir}/qtwebengine_locales/zh-TW.pak

%files devel
%{_qt5_headerdir}/Qt*/
%{_qt5_libdir}/libQt5*.so
%{_qt5_libdir}/libQt5*.prl
%{_qt5_libdir}/cmake/Qt5*/
%{_qt5_libdir}/pkgconfig/Qt5*.pc
%{_qt5_archdatadir}/mkspecs/modules/*.pri

%files examples
%{_qt5_examplesdir}/

%if 0%{?docs}
%files doc
%{_qt5_docdir}/*
%endif


%changelog
* Sun Jul 31 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.1-4
- BR: cmake (for cmake autoprovides mostly)

* Tue Jun 14 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.1-3
- rebuild (glibc)

* Sun Jun 12 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.1-2
- add versioned qt5-qtbase runtime dep

* Sat Jun 11 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.1-1
- Update to 5.6.1
- Rebase linux-pri patch (drop the parts already fixed upstream)
- Drop backported chimera-nss-init patch, already applied upstream
- Rebase no-sse2 patch (the core_module.pro change)
- Add the new designer/libqwebengineview.so plugin to the file list

* Mon Jun 06 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-8
- workaround stackmashing runtime errors in re2-related bundled headers (#1337585)

* Sat May 21 2016 Rex Dieter <rdieter@fedoraproject.org> - 5.6.0-7
- rebuild (pciutuils)

* Wed May 18 2016 Rex Dieter <rdieter@fedoraproject.org> 5.6.0-6
- BR: git-core

* Fri Apr 15 2016 David Tardon <dtardon@redhat.com> - 5.6.0-5
- rebuild for ICU 57.1

* Fri Apr 08 2016 Than Ngo <than@redhat.com> - 5.6.0-4
- drop ppc ppc64 ppc64le from ExclusiveArch, it's not supported yet

* Thu Mar 24 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-3
- Build with CONFIG+="webcore_debug v8base_debug force_debug_info"
- Force -fno-delete-null-pointer-checks through CXXFLAGS, Qt flags not used here
- Use -g1 instead of -g on non-x86_64 to avoid memory exhaustion
- Work around debugedit failure by removing "./" from #line commands and
  changing "//" to "/" in an #include command

* Fri Mar 18 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-2
- Avoid checking for the nonexistent icudtl.dat and silence the warnings

* Thu Mar 17 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-1
- Update to 5.6.0 (final)
- Drop system-icu54 patch, fixed upstream

* Thu Feb 25 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.19.rc
- Update to 5.6.0 RC
- Rebase linux-pri and no-sse2 patches
- Remove BuildRequires pkgconfig(flac), pkgconfig(speex), no longer needed
- Update file list for 5.6.0 RC (resources now in resources/ subdirectory)
- Tag translations with correct %%lang tags

* Wed Feb 24 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.18.beta
- no-sse2 patch: Fix FFT (RealFourier) in webrtc on non-SSE2 x86

* Tue Feb 23 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.17.beta
- Fix FTBFS on aarch64: Respin tarball with fixed clean_ffmpeg.sh (#1310753).

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 5.6.0-0.16.beta
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 19 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.15.beta
- Build V8 as a shared library on i686 to allow for swappable backends
- Build both the x87 version and the SSE2 version of V8 on i686
- Add the private library directory to the file list on i686
- Add Provides/Requires filtering for libv8.so (i686) and for plugins

* Sun Jan 17 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.14.beta
- Do not require SSE2 on i686

* Thu Jan 14 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.13.beta
- Drop nss321 backport (and the related nss-headers patch), it did not help
- Do an NSS/BoringSSL "chimera build" as will be the default in Chromium 47
- Update License accordingly (add "OpenSSL")
- Fix the "chimera build" to call EnsureNSSHttpIOInit (backport from Chromium)

* Wed Jan 13 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.12.beta
- Update forked NSS SSL code to 3.21, match system NSS (backport from Chromium)

* Wed Jan 13 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.11.beta
- Add an (optimistic) ExclusiveArch list because of V8 (tracking bug: #1298011)

* Tue Jan 12 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.10.beta
- Unbundle prtime.cc, use the system NSPR instead (which is already required)
- Unbundle icu_utf.cc, use the system ICU instead (which is already required)

* Mon Jan 11 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.9.beta
- linux-pri.patch: Set icu_use_data_file_flag=0 for system ICU

* Mon Jan 11 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.8.beta
- Build against the system libvpx also on F23 (1.4.0), worked in Copr

* Mon Jan 11 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.7.beta
- Use the system libvpx on F24+ (1.5.0)
- Fixes to Provides: bundled(*): libwebp if bundled, x86inc only on x86

* Sun Jan 10 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.6.beta
- Fix extractCFlag to also look in QMAKE_CFLAGS_RELEASE (needed for ARM)
- Fix FTBFS on ARM: Disable NEON due to #1282495 (GCC bug)

* Sat Jan 09 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.5.beta
- Fix FTBFS on ARM: linux-pri patch: Set use_system_yasm only on x86_64 and i386
- Fix FTBFS on ARM: Respin tarball with: clean_ffmpeg.sh: Add missing ARM files

* Sat Jan 09 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.4.beta.1
- Use more specific BuildRequires for docs (thanks to rdieter)
- Fix FTBFS against ICU 54 (F22/F23), thanks to spot for the Chromium fix

* Fri Jan 08 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.4.beta
- Fix License tag
- Use %%_qt5_examplesdir macro
- Add Provides: bundled(*) for all the bundled libraries that I found

* Wed Jan 06 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.3.beta
- linux-pri patch: Add use_system_protobuf, went missing in the 5.6 rebase

* Wed Jan 06 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.2.beta
- linux-pri patch: Add missing newline at the end of the log line
- Use export for NINJA_PATH (fixes system ninja-build use)

* Wed Jan 06 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.6.0-0.1.beta
- Readd BR pkgconfig(jsoncpp) because linux.pri now checks for it
- BR yasm only on x86 (i686, x86_64)
- Add dot at the end of %%description
- Rebase no-format patch
- Replace unbundle-gyp.patch with new linux-pri.patch
- Use system ninja-build instead of the bundled one
- Run the unbundling script replace_gyp_files.py in linux.pri rather than here
- Update file list for 5.6.0-beta (no more libffmpegsumo since Chromium 45)

* Tue Jan 05 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.5.1-4
- Remove unused BRs flex, libgcrypt-devel, bzip2-devel, pkgconfig(gio-2.0),
  pkgconfig(hunspell), pkgconfig(libpcre), pkgconfig(libssl),
  pkgconfig(libcrypto), pkgconfig(jsoncpp), pkgconfig(libmtp),
  pkgconfig(libexif), pkgconfig(liblzma), pkgconfig(cairo), pkgconfig(libusb),
  perl(version), perl(Digest::MD5), perl(Text::ParseWords), ruby
- Add missing explicit BRs on pkgconfig(x11),  pkgconfig(xext),
  pkgconfig(xfixes), pkgconfig(xdamage), pkgconfig(egl)
- Fix BR pkgconfig(flac++) to pkgconfig(flac) (libFLAC++ not used, only libFLAC)
- Fix BR python-devel to python
- Remove unused -Duse_system_openssl=1 flag (QtWebEngine uses NSS instead)
- Remove unused -Duse_system_jsoncpp=1 and -Duse_system_libusb=1 flags

* Mon Jan 04 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.5.1-3
- Update file list for 5.5.1 (add qtwebengine_resources_[12]00p.pak)

* Mon Jan 04 2016 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.5.1-2
- Add missing explicit BRs on pkgconfig(expat) and pkgconfig(libxml-2.0)
- Remove unused BR v8-devel (cannot currently be unbundled)

* Thu Dec 24 2015 Kevin Kofler <Kevin@tigcc.ticalc.org> - 5.5.1-1
- Update to 5.5.1
- Remove patent-encumbered codecs in the bundled FFmpeg from the tarball

* Fri Jul 17 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.0-2
- Update with unbundle flags. Adapted from original 5.4 Suse package
- Disable vpx and sqlite as unbundle due some compilation issues
- Enable verbose build

* Fri Jul 17 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.0-1
- Initial spec

* Thu Jun 25 2015 Helio Chissini de Castro <helio@kde.org> - 5.5.0-0.2.rc
- Update for official RC1 released packages
