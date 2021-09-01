import urllib.request

from tuxemon.constants import paths
import pathlib
import os
import json
import zipfile
import shutil

class Manager:

    def __init__(self, *other_urls, default_to_cache=True):
        """
        (basic) Mod managment library.
        """
        # TODO: Recreate the __init__
        # TODO: Cache updates by default


        if len(other_urls) == 0:
            other_urls = ["http://127.0.0.1:5000"]

        self.packages_path = os.path.join(paths.CACHE_DIR, "packages")

        self.url = other_urls
        self.packages = []

        if default_to_cache:
            self.packages = self.read_from_cache()

    def write_to_cache(self):
        """Writes self.packages to the cache file"""

        with open(self.packages_path, "w") as file:
            file.write(
                json.dumps(self.packages, indent=4)
            )
    def read_from_cache(self):
        """Read self.packages from the cache file"""
        with open(self.packages_path) as file:
            return json.loads(file.read())

    def cache_to_pkglist(self):
        """
        Override self.packages with the cache.
        Uses self.packages = self.read_from_cache()
        """
        self.packages = self.read_from_cache()

    def update(self, url):
        """Returns the response from the server"""
        with urllib.request.urlopen(url + "/api/packages") as packages:
            return json.loads(packages.read().decode("UTF-8"))

    def update_all(self):
        """
        Updates all packages in self.package.
        It automatically clears the self.package variable, and then
        populates it from the data from the repositories.
        """
        self.packages = []

        for i in self.url:
            for package in self.update(i):
                self.packages.append(package)

        self.write_to_cache()

    def list_packages(self):
        """Returns package dictionary, either from the server or the cache"""
        return self.packages

    def download_package(self, name, release, repo=None, dont_extract=False):
        """Downloads the specified package"""
        print(name, release, repo)
        if repo is None:
            repo = self.get_package_repo(name)

            # Remove trailing slash
            if repo[-1] == "/":
                repo = repo[:-1]
        
        url = str(repo) + f"/packages/{name}/releases/{str(release)}/download"
        filename = os.path.join(paths.CACHE_DIR + f"/{name}.{release}.zip")

        # Apperantly this function is ported from urllib from python2.
        # Maybe replace this in the future?
        # https://docs.python.org/3/library/urllib.request.html#urllib.request.urlretrieve
        urllib.request.urlretrieve(url, filename=filename) 

        outfolder = os.path.join(paths.BASEDIR, "mods", f"{name}")

        self.write_package_to_list(outfolder, name)

        if not dont_extract:
            self.extract(filename, outfolder)
            with open(f"{outfolder}/meta.json", "w") as metafile:
                meta = self.get_package_info(name, repo)
                metafile.write(json.dumps(meta, indent=4))

    def download_packages(self, name, release, repo, dont_extract=False):
        """Same as the download_package(), but it includes dependency installing"""
        # Get info
        meta = self.get_package_info(author, name, repo)
        if "depends" in meta:
            dependencies = meta["dependencies"]

            for pack in dependencies:
               pass

    def extract(self, file, outfolder):
        """Extracts the specified zip archive to the mods directory"""
        with zipfile.ZipFile(file) as zip_:
            zip_.extractall(path=os.path.join(paths.BASEDIR, "mods", outfolder))

    def get_package_info(self, name, repo):
        """Get specified package info. Always downloads the info from the server."""
        with urllib.request.urlopen(repo + f"/api/packages/{name}") as packages:
            return json.loads(packages.read().decode("UTF-8"))

    def get_package_repo(self, name):
        """Reads the origin of an package.
        Returns None, if key 'mods' doesn't exist"""
        #print()
        for i in self.packages:
            if i["name"] == name:
                print(i)
                return i["repo"]
                """
                if "repo" in i: return i["repo"]
                else: return None
                """
            else: print(f"{i} not in the name")

    def write_package_to_list(self, path_to_folder, name):
        """Writes specified package to the package list"""
        # Write the absolute path to the list
        with open(paths.USER_GAME_DATA_DIR + "/package.list", "w+") as file:
            if not len(file.read()) == 0:
                before = json.loads(file.read())
            else:
                before = {}

            to_append = {name: path_to_folder}
            after = {**before, **to_append}
            file.write(
                json.dumps(after, indent=4)
            )

    def read_package_from_list(self, name):
        """Reads path of the specified mod"""
        #try:
        with open(paths.USER_GAME_DATA_DIR + "/package.list") as file:
            data = file.read()
            print(f"DEBUG_READPKG: {data}\n{paths.USER_GAME_DATA_DIR + '/package.list'}")
            return json.loads(data)[name]
            """else:
                print("Empty")
                return None
                #raise ValueError"""
        #except (FileNotFoundError, ValueError) as e:
        #    print(e, "Error")
        #    return None

    def remove_package_from_list(self, name):
        """Removes specified package from the package list"""
        # Write the absolute path to the list
        with open(paths.USER_GAME_DATA_DIR + "/package.list", "r+") as file:
            data = file.read()
            if not len(data) == 0:
                before = json.loads(data)
            else:
                raise ValueError("The package.list is empty.")

            del before[name]
            file.write(
                json.dumps(before, indent=4)
            )


    def remove_package(self, name):
        """Removes the local package"""
        # Get the path
        path = self.read_package_from_list(name)

        shutil.rmtree(path, ignore_errors=True)
        self.remove_package_from_list(name)
