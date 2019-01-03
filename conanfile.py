from conans import ConanFile, tools, MSBuild
from conanos.build import config_scheme
import os, shutil

class X265Conan(ConanFile):
    name = "x265"
    version = "2.8"
    description = "x265 is an open-source project and free application library for encoding video streams into the H.265/High Efficiency Video Coding (HEVC) format"
    url = "https://github.com/conanos/x265"
    homepage = "http://www.x265.org/","https://github.com/videolan/x265"
    license = "GPL-2.0"
    generators = "gcc","visual_studio"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        'fPIC': [True, False]
    }
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        url_ = 'https://github.com/ShiftMediaProject/x265/archive/{version}.tar.gz'
        tools.get(url_.format(version=self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"SMP")):
                msbuild = MSBuild(self)
                build_type = str(self.settings.build_type) + ("DLL" if self.options.shared else "")
                msbuild.build("libx265.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'},build_type=build_type)

    def package(self):
        if self.settings.os == 'Windows':
            platforms={'x86': 'Win32', 'x86_64': 'x64'}
            rplatform = platforms.get(str(self.settings.arch))
            self.copy("*", dst=os.path.join(self.package_folder,"include"), src=os.path.join(self.build_folder,"..", "msvc","include"))
            if self.options.shared:
                for i in ["lib","bin"]:
                    self.copy("*", dst=os.path.join(self.package_folder,i), src=os.path.join(self.build_folder,"..","msvc",i,rplatform))
            self.copy("*", dst=os.path.join(self.package_folder,"licenses"), src=os.path.join(self.build_folder,"..", "msvc","licenses"))

            tools.mkdir(os.path.join(self.package_folder,"lib","pkgconfig"))
            shutil.copy(os.path.join(self.build_folder,self._source_subfolder,"source","x265.pc.in"),
                        os.path.join(self.package_folder,"lib","pkgconfig","x265.pc"))
            lib = "-lx265d" if self.options.shared else "-lx265"
            replacements = {
                "@CMAKE_INSTALL_PREFIX@" : self.package_folder,
                "@LIB_INSTALL_DIR@"      : "lib",
                "@CMAKE_PROJECT_NAME@"   : self.name,
                "@X265_LATEST_TAG@"      : self.version,
                "@PRIVATE_LIBS@"         : "",
                "-lx265"                 : lib
            }
            for s, r in replacements.items():
                tools.replace_in_file(os.path.join(self.package_folder,"lib","pkgconfig","x265.pc"),s,r)

    def package_info(self):
        self.cpp_info.libs = ["hello"]

