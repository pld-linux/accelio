# TODO:
# - kernel modules (BR: OFED kernel headers)
#
# Conditional build:
%bcond_without	fio		# FIO module
%bcond_with	kernel		# kernel modules
%bcond_without	static_libs	# static libraries
#
Summary:	Open Source I/O, Message and RPC Acceleration library
Summary(pl.UTF-8):	Mająca otwarte źródła biblioteka przyspieszająca we/wy, komunikaty i RPC
Name:		accelio
Version:	1.6
Release:	1
License:	BSD
Group:		Libraries
Source0:	https://github.com/accelio/accelio/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	0f6634e03ff1bf2e9b83e554202d093f
Patch0:		%{name}-fio.patch
Patch1:		%{name}-sse.patch
URL:		http://www.accelio.org/
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake >= 1:1.11
%{?with_fio:BuildRequires:	fio-devel >= 2.8}
BuildRequires:	libaio-devel
BuildRequires:	libevent-devel >= 2
BuildRequires:	libibverbs-devel
BuildRequires:	libtool >= 2:2
BuildRequires:	numactl-devel
BuildRequires:	sed >= 4.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Accelio provides an easy-to-use, reliable, scalable, and high
performance data/message delivery middleware that maximizes the
efficiency of modern CPU and NIC hardware and that reduces
time-to-market of new scale-out applications.

%description -l pl.UTF-8
Accelio dostarcza łatwą w użyciu, wiarygodną, skalowalną i szybką
warstwę pośrednią przekazującą dane i komunikaty, maksymalizującą
wydajność współczesnych CPU i NIC, zmniejszającą czas potrzebny
na wytworzenie nowych aplikacji.

%package devel
Summary:	Header files for Accelio libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek Accelio
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for Accelio libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek Accelio.

%package static
Summary:	Static Accelio libraries
Summary(pl.UTF-8):	Statyczne biblioteki Accelio
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static Accelio libraries.

%description static -l pl.UTF-8
Statyczne biblioteki Accelio.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%{__sed} -i -e 's/-Werror //' configure.ac

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
for d in src/kernel/xio examples/kernel/hello_world examples/kernel/hello_world_mt tests/kernel/hello_test examples/raio/kernel/nbdx ; do
cd $d
%{__autoconf}
cd -
done
%configure \
	%{?with_fio:FIO_ROOT=%{_includedir}/fio} \
	--disable-silent-rules \
	%{!?with_static_libs:--disable-static} \
	%{?with_fio:--enable-fio-build} \
	%{?with_kernel:--enable-kernel-module}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# fio module, .la is useless
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libraio_fio.la
# test program
%{__rm} $RPM_BUILD_ROOT%{_bindir}/event_loop_tests

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog NEWS README README.md
%attr(755,root,root) %{_bindir}/raio_client
%attr(755,root,root) %{_bindir}/raio_server
%attr(755,root,root) %{_bindir}/reg_basic_mt
%attr(755,root,root) %{_bindir}/xio_*
%attr(755,root,root) %{_bindir}/xioclntd
%attr(755,root,root) %{_bindir}/xiosrvd
%attr(755,root,root) %{_libdir}/libraio.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libraio.so.0
%if %{with fio}
%attr(755,root,root) %{_libdir}/libraio_fio.so
%endif
%attr(755,root,root) %{_libdir}/libxio.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libxio.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libraio.so
%attr(755,root,root) %{_libdir}/libxio.so
%{_libdir}/libraio.la
%{_libdir}/libxio.la
%{_includedir}/libraio.h
%{_includedir}/libxio.h
%{_includedir}/xio_base.h
%{_includedir}/xio_predefs.h
%{_includedir}/xio_user.h

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libraio.a
%{_libdir}/libxio.a
%endif
