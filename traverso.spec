%global sse_cxxflags %{optflags}
%global sse_cmakeflags -DHOST_SUPPORTS_SSE:BOOL=FALSE
%ifarch %{ix86}
%global with_sse %{!?_without_sse:1}%{?_without_sse:0}
%if %{with_sse}
%global sse_cxxflags -DSSE_OPTIMIZATIONS -DARCH_X86 %{optflags}
%global sse_cmakeflags -DHOST_SUPPORTS_SSE:BOOL=TRUE -DIS_ARCH_X86:BOOL=TRUE
%endif
%endif
%ifarch ia64 x86_64
%global with_sse 1
%global sse_cxxflags -DSSE_OPTIMIZATIONS -DUSE_XMMINTRIN -DARCH_X86 -DUSE_X86_64_ASM %{optflags}
%global sse_cmakeflags -DHOST_SUPPORTS_SSE:BOOL=TRUE -DIS_ARCH_X86_64:BOOL=TRUE
%endif

Name:           traverso
Version:        0.49.3
Release:        6%{?dist}
Summary:        Multitrack Audio Recording and Editing Suite
Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://traverso-daw.org/
# Source0 actually is http://traverso-daw.org/download.html&d=%{name}-%{version}.tar.gz
# but rpmbuild doesn't work with this kind of URL's. So
Source0:        %{name}-%{version}.tar.gz
# lower the rtprio requirement to 20, for compliance with our jack
Patch0:         %{name}-priority.patch
# Fix DSO linking
Patch1:         traverso-gcc49.patch
Patch2:         gcc6-buildfix-01.patch
BuildRequires:  alsa-lib-devel
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  fftw-devel
BuildRequires:  flac-devel
BuildRequires:  jack-audio-connection-kit-devel
BuildRequires:  lame-devel
BuildRequires:  lilv-devel
BuildRequires:  libmad-devel
BuildRequires:  libogg-devel
BuildRequires:  libsamplerate-devel
BuildRequires:  libsndfile-devel
BuildRequires:  libvorbis-devel
BuildRequires:  portaudio-devel
# Native pulseaudio is not supported yet.
#BuildRequires:  pulseaudio-libs-devel
BuildRequires:  qt-devel
BuildRequires:  raptor-devel
BuildRequires:  redland-devel
BuildRequires:  wavpack-devel

# For directory ownership:
Requires:       hicolor-icon-theme
Requires:       shared-mime-info

%description
Traverso Digital Audio Workstation is a cross platform multitrack audio 
recording  and editing suite, with an innovative and easy to master User
Interface. It's suited for both the professional and home user, who needs a
robust and solid DAW. 

Traverso is a complete solution from recording to CD Mastering. By supplying
many common tools in one package, you don't have to learn how to use lots of
applications with different user interfaces. This considerably lowers the 
learning curve, letting you get your audio processing work done faster!

A unique approach to non-linear audio processing was developed for Traverso to
provide extremely solid and robust audio processing and editing. Adding and 
removal of effects plugins, moving Audio Clips and creating new Tracks during 
playback are all perfectly safe, giving you instant feedback on your work! 

%prep
%setup -q
%patch0 -p1 -b .priority
%patch1 -p1 -b .gcc49
%patch2 -p1 -b .gcc6


# Fix permission issues
chmod 644 ChangeLog TODO
for ext in h cpp; do
   find . -name "*.$ext" -exec chmod 644 {} \;
done

# To match the freedesktop standards
sed -i -e '\|^MimeType=.*[^;]$|s|$|;|' \
    resources/%{name}.desktop

# We use the system slv2, so just to make sure
rm -fr src/3rdparty/slv2

# For proper slv2 detection
sed -i 's|libslv2|slv2|g' CMakeLists.txt


%build
# Build the actual program
%{cmake}                                               \
         -DWANT_MP3_ENCODE=ON                          \
         -DUSE_SYSTEM_SLV2_LIBRARY=ON                  \
         -DDETECT_HOST_CPU_FEATURES=OFF                \
         -DWANT_PORTAUDIO=ON                           \
         -DCXX_FLAGS:STRING="%{sse_cxxflags}"          \
         %{sse_cmakeflags}                             \
         .

make %{?_smp_mflags} VERBOSE=1 

# Add Comment to the .desktop file
echo "Comment=Digital Audio Workstation" >> resources/%{name}.desktop


%install
make install DESTDIR=%{buildroot} 

# icons
install -dm 755 %{buildroot}%{_datadir}/icons/hicolor/
cp -a resources/freedesktop/icons/* %{buildroot}%{_datadir}/icons/hicolor/

# desktop file
install -dm 755 %{buildroot}%{_datadir}/applications/
desktop-file-install                          \
   --dir %{buildroot}%{_datadir}/applications \
   --remove-mime-type=text/plain              \
   --add-mime-type=application/x-traverso     \
   --add-category=X-Multitrack                \
   --add-category=Sequencer                   \
   --remove-key=Path                          \
   resources/%{name}.desktop

# mime-type file
install -dm 755 %{buildroot}%{_datadir}/mime/packages/
install -pm 644 resources/x-%{name}.xml %{buildroot}%{_datadir}/mime/packages/

%post
update-desktop-database &> /dev/null
touch --no-create %{_datadir}/icons/hicolor &>/dev/null
update-mime-database %{_datadir}/mime &> /dev/null || :

%postun
update-desktop-database &> /dev/null
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null
fi
update-mime-database %{_datadir}/mime &> /dev/null || :

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%doc AUTHORS ChangeLog COPYING COPYRIGHT HISTORY README TODO
%doc resources/projectconversion/2_to_3.html resources/help.text
%{_bindir}/%{name}
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/mime/packages/*.xml

%changelog
* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.49.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Mar 01 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 0.49.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 0.49.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Mar 20 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 0.49.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jul 19 2016 Leigh Scott <leigh123linux@googlemail.com> - 0.49.3-2
- patch for gcc-6

* Fri Nov 28 2014 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.3-1
- Update to 0.49.3

* Sun Aug 31 2014 Sérgio Basto <sergio@serjux.com> - 0.49.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Mar 03 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.49.2-6
- Mass rebuilt for Fedora 19 Features

* Thu May 03 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.49.2-5
- Fix for gcc47 and missing cflags

* Fri Mar 02 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.49.2-4
- Rebuilt for c++ ABI breakage

* Wed Feb 08 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.49.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Aug 21 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.49.2-2
- rebuilt

* Fri Aug 13 2010 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.2-1
- Update to 0.49.2

* Wed May 06 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.1-7
- Explicitly disable SSE optimizations on non-"%%{ix86} ia64 x86_64" architectures

* Wed May 06 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.1-6
- Re-enable portaudio

* Fri May 01 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.1-5
- Patch for dropping the rtprio requirement of traverso
- Drop the limits config file
- Drop the warnings patch

* Tue Apr 28 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.1-4
- Drop the defaults patch
- Fix slv2 library detection
- Add traversouser group
- Install limits config file in /etc/security/limits.d/

* Mon Apr 27 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.1-3
- Remove the supplied slv2 library in %%prep
- Add versioned BR to slv2 (>= 0.6.1)
- Drop the pdf manual
- Introduce new patch to handle the sse optimizations

* Thu Apr 16 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.1-2
- Change the default number of periods from 3 to 2
- Give a more verbose output if sound doesn't work
- Add the manual

* Sun Mar 29 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.1-1
- New upstream release
- Fix the year of the previous changelog entries
- Drop portaudio support. Upstream says that is unnecessary
- Drop pulseaudio support. Upstream says it is not ready yet
- Use system slv2 library instead of the shipped one

* Mon Mar 16 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.0-2
- Add disttag
- Disable automatic host cpu features detection while building and manually select 
  the cpu related flags
- Minor adjustment in %%postun: Use "|| :" only in the last command
- Minor adjustment in the .desktop file: Add trailing ";" to MimeType

* Sun Mar 15 2009 Orcan Ogetbil <oget [DOT] fedora [AT] gmail [DOT] com> - 0.49.0-1
- Initial build
