# -*- coding: utf-8 -*-
"""
v0.5
  - convert to API 0.5
  - temporary removed rich html support due https://github.com/albertlauncher/albert/issues/1164
v0.6
  - convert to API 2.1
"""

import json
from pathlib import Path
from shutil import which
from typing import List, Literal, Optional, Tuple
from albert import *


md_name = "Visual Studio Code"
md_iid = "2.1"
md_description = "Open & search recent Visual Studio Code files and folders."
md_id = "vs"
md_version = "0.6"
md_maintainers = ["@mparati31", "@bierchermuesli"]
md_url = "https://github.com/mparati31/albert-vscode"


class Plugin(PluginInstance, GlobalQueryHandler):
    ICON_PROJECT = [f"file:{Path(__file__).parent}/icon_project.png"]
    ICON = [f"file:{Path(__file__).parent}/icon.png"]
    VSCODE_PROJECTS_PATH = Path.home() / ".config" / "Code" / "User" / "globalStorage" / 'alefragnani.project-manager' / 'projects.json'
    VSCODE_RECENT_PATH = Path.home() / ".config" / "Code" / "User" / "globalStorage" / "storage.json"
    EXECUTABLE = which("code")

    def __init__(self):
        GlobalQueryHandler.__init__(self, id=md_id, name=md_name, description=md_description, defaultTrigger="vs ")
        PluginInstance.__init__(self, extensions=[self])

    # Returns the following tuple: (recent files paths, recent folders paths).
    def get_visual_studio_code_recent(
        self,
    ) -> Tuple[List[str], List[str]]:
        storage = json.load(open(self.VSCODE_RECENT_PATH, "r"))
        menu_items = storage["lastKnownMenubarData"]["menus"]["File"]["items"]
        file_menu_items = list(filter(lambda item: item["id"] == "submenuitem.MenubarRecentMenu", menu_items))
        submenu_recent_items = file_menu_items[0]["submenu"]["items"]
        files = list(filter(lambda item: item["id"] == "openRecentFile", submenu_recent_items))
        folders = list(filter(lambda item: item["id"] == "openRecentFolder", submenu_recent_items))
        extract_path = lambda item: item["uri"]["path"]
        files_paths = list(map(extract_path, files))
        folders_paths = list(map(extract_path, folders))
        return files_paths, folders_paths

    # Return favorite projects
    def get_favorite_projects(self) -> List[dict]:
        try:
            projects_path = self.VSCODE_PROJECTS_PATH
            if not projects_path.exists():
                return []

            with open(projects_path, 'r') as f:
                projects = json.load(f)

            return projects
        except Exception as e:
            warning(f"Error reading Project Manager settings: {str(e)}")
            return []

    # Returns the abbreviation of `path` that has `maxchars` character size.
    def resize_path(self, path: str | Path, maxchars: int = 45) -> str:
        filepath = Path(path)
        if len(str(filepath)) <= maxchars:
            return str(filepath)
        else:
            parts = filepath.parts
            # If the path is contains only the pathname, then it is returned as is.
            if len(parts) == 1:
                return str(filepath)
            relative_len = 0
            short_path = ""
            # Iterates on the reverse path elements and adds them until the relative
            # path exceeds `maxchars`.
            for part in reversed(parts):
                if len(part) == 0:
                    continue
                if len(".../{}/{}".format(part, short_path)) <= maxchars:
                    short_path = "/{}{}".format(part, short_path)
                    relative_len += len(part)
                else:
                    break
            return "...{}".format(short_path)

    # Return a item.
    def make_item(self, text: str, subtext: str = "", actions: List[Action] = []) -> Item:
        return StandardItem(id=md_id, iconUrls=self.ICON, text=text, subtext=subtext, actions=actions)

    # Return an item that create a new window.
    def make_new_window_item(self) -> StandardItem:
        return self.make_item(
            "New Empty Window", "Open new Visual Studio Code empty window", [Action(id=md_id, text="Open in Visual Studio Code", callable=lambda: runDetachedProcess(cmdln=[self.EXECUTABLE]))]
        )

    # Return a recent item.
    def make_recent_item(self, path: str | Path, recent_type: Literal["file", "folder"]) -> Item:
        resized_path = self.resize_path(path)
        path_splits = resized_path.split("/")
        working_dir_path, filename = path_splits[:-1], path_splits[-1]
        formatted_path = "{}/{}".format("/".join(working_dir_path), filename)

        return self.make_item(
            formatted_path, "Open Recent {}".format(recent_type), [Action(id=path, text="Open in Visual Studio Code", callable=lambda: runDetachedProcess(cmdln=[self.EXECUTABLE, path]))]
        )

    # Return a recent item.
    def make_project_item(self, path: str | Path, name: str) -> Item:
        resized_path = self.resize_path(path)
        path_splits = resized_path.split("/")
        working_dir_path, filename = path_splits[:-1], path_splits[-1]
        formatted_path = "{}/{}".format("/".join(working_dir_path), filename)

        return StandardItem(
            id=md_id, iconUrls=self.ICON_PROJECT, text=name, subtext=formatted_path,
            actions=[Action(id=path, text="Open in Visual Studio Code",
                            callable=lambda: runDetachedProcess(cmdln=[self.EXECUTABLE, path]))]
        )

    def handleTriggerQuery(self, query) -> Optional[List[Item]]:
        if not self.EXECUTABLE:
            return query.add(self.make_item("Visual Studio Code not installed"))

        query_text = query.string

        debug("query: '{}'".format(query_text))

        query_text = query_text.strip().lower()
        files, folders = self.get_visual_studio_code_recent()
        projects = self.get_favorite_projects()

        debug("vs recent files: {}".format(files))
        debug("vs recent folders: {}".format(folders))

        items = []
        if query_text in "New Empty Window".lower():
            items.append(query.add(self.make_new_window_item()))

        for project in projects:
            project_name = project.get('name', '')
            project_path = project.get('rootPath', '')

            if not project_name or not project_path:
                continue

            if not project_path.startswith(('vscode:', 'file:')):
                project_path = f"file://{project_path}"

            fs_path = project_path.replace('file://', '', 1).replace('vscode://', '', 1)
            item = self.make_project_item(fs_path, project_name)
            items.append(query.add(item))

        if not folders and not files:
            items.append(query.add(self.make_item("Recent Files and Folders not found")))
            return items

        for element_name in folders + files:
            if query_text not in element_name.lower():
                continue
            else:
                item = query.add(self.make_recent_item(element_name, "folder" if element_name in folders else "file"))
            items.append(item)

        return items
