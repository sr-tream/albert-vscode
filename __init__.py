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
import subprocess

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
        self._mode = self.readConfig("mode", str)
        if self._mode is None:
            self._mode = "VSCode"
        else:
            self.updateMode()
        
        # Initialize git worktree settings
        self._extract_worktrees = self.readConfig("extract_worktrees", bool) or False
        self._git_executable = self.readConfig("git_executable", str) or "git"

    def configWidget(self):
        return [
            {"type": "label", "text": "Select Mode:"},
            {
                "type": "combobox",
                "label": "Mode",
                "property": "mode",
                "items": ["VSCode", "VSCode - Insiders", "VSCodium", "VSCodium - Insiders", "Cursor", "Windsurf"],
                "widget_properties": {
                    "currentIndex": 0 if self.mode == "VSCode" else 1
                },
            },
            {"type": "label", "text": "Git Settings:"},
            {
                "type": "checkbox",
                "label": "Extract Git Worktrees",
                "property": "extract_worktrees",
                "value": self._extract_worktrees
            },
            {
                "type": "lineedit",
                "label": "Git Executable Path",
                "property": "git_executable",
                "value": self._git_executable
            },
        ]

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.writeConfig("mode", value)
        self.updateMode()

    @property
    def extract_worktrees(self):
        return self._extract_worktrees

    @extract_worktrees.setter
    def extract_worktrees(self, value):
        self._extract_worktrees = value
        self.writeConfig("extract_worktrees", value)

    @property
    def git_executable(self):
        return self._git_executable

    @git_executable.setter
    def git_executable(self, value):
        self._git_executable = value
        self.writeConfig("git_executable", value)

    def updateMode(self):
        if self.mode == "VSCode":
            self.ICON_PROJECT = [f"file:{Path(__file__).parent}/icon_project.png"]
            self.ICON = [f"file:{Path(__file__).parent}/icon.png"]
            self.VSCODE_RECENT_PATH = (
                Path.home()
                / ".config"
                / "Code"
                / "User"
                / "globalStorage"
                / "storage.json"
            )
            self.VSCODE_PROJECTS_PATH = (
                Path.home()
                / ".config"
                / "Code"
                / "User"
                / "globalStorage"
                / "alefragnani.project-manager"
                / "projects.json"
            )
            self.EXECUTABLE = (
                which("code") or ""
            )
        elif self.mode == "VSCode - Insiders":
            self.ICON_PROJECT = [f"file:{Path(__file__).parent}/icon_project.png"]
            self.ICON = [f"file:{Path(__file__).parent}/icon.png"]
            self.VSCODE_RECENT_PATH = (
                Path.home()
                / ".config"
                / "Code - Insiders"
                / "User"
                / "globalStorage"
                / "storage.json"
            )
            self.VSCODE_PROJECTS_PATH = (
                Path.home()
                / ".config"
                / "Code - Insiders"
                / "User"
                / "globalStorage"
                / "alefragnani.project-manager"
                / "projects.json"
            )
            self.EXECUTABLE = (
                which("code-insiders") or ""
            )
        elif self.mode == "VSCodium":
            self.ICON_PROJECT = [f"file:{Path(__file__).parent}/codium-icon_project.png"]
            self.ICON = [f"file:{Path(__file__).parent}/codium-icon.png"]
            self.VSCODE_RECENT_PATH = (
                Path.home()
                / ".config"
                / "VSCodium"
                / "User"
                / "globalStorage"
                / "storage.json"
            )
            self.VSCODE_PROJECTS_PATH = (
                Path.home()
                / ".config"
                / "VSCodium"
                / "User"
                / "globalStorage"
                / "alefragnani.project-manager"
                / "projects.json"
            )
            self.EXECUTABLE = (
                which("codium") or ""
            )
        elif self.mode == "VSCodium - Insiders":
            self.ICON_PROJECT = [f"file:{Path(__file__).parent}/codium-insiders-icon_project.png"]
            self.ICON = [f"file:{Path(__file__).parent}/codium-insiders-icon.png"]
            self.VSCODE_RECENT_PATH = (
                Path.home()
                / ".config"
                / "VSCodium - Insiders"
                / "User"
                / "globalStorage"
                / "storage.json"
            )
            self.VSCODE_PROJECTS_PATH = (
                Path.home()
                / ".config"
                / "VSCodium - Insiders"
                / "User"
                / "globalStorage"
                / "alefragnani.project-manager"
                / "projects.json"
            )
            self.EXECUTABLE = (
                which("codium-insiders") or ""
            )
        elif self.mode == "Cursor":
            self.ICON_PROJECT = [f"file:{Path(__file__).parent}/cursor-icon_project.png"]
            self.ICON = [f"file:{Path(__file__).parent}/cursor-icon.png"]
            self.VSCODE_RECENT_PATH = (
                Path.home()
                / ".config"
                / "Cursor"
                / "User"
                / "globalStorage"
                / "storage.json"
            )
            self.VSCODE_PROJECTS_PATH = (
                Path.home()
                / ".config"
                / "Cursor"
                / "User"
                / "globalStorage"
                / "alefragnani.project-manager"
                / "projects.json"
            )
            self.EXECUTABLE = (
                which("cursor") or which("cursor.AppImage") or ""
            )
        else:
            self.ICON_PROJECT = [
                f"file:{Path(__file__).parent}/windsurf-icon_project.png"
            ]
            self.ICON = [f"file:{Path(__file__).parent}/windsurf-icon.png"]
            self.VSCODE_RECENT_PATH = (
                Path.home()
                / ".config"
                / "Windsurf"
                / "User"
                / "globalStorage"
                / "storage.json"
            )
            self.VSCODE_PROJECTS_PATH = (
                Path.home()
                / ".config"
                / "Windsurf"
                / "User"
                / "globalStorage"
                / "alefragnani.project-manager"
                / "projects.json"
            )
            self.EXECUTABLE = which("windsurf") or ""

    # Returns the following tuple: (recent files paths, recent folders paths).
    def get_visual_studio_code_recent(
        self,
    ) -> Tuple[List[str], List[str], List[str]]:
        storage = json.load(open(self.VSCODE_RECENT_PATH, "r"))
        menu_items = storage["lastKnownMenubarData"]["menus"]["File"]["items"]
        file_menu_items = list(filter(lambda item: item["id"] == "submenuitem.MenubarRecentMenu", menu_items))
        submenu_recent_items = file_menu_items[0]["submenu"]["items"]
        files = list(filter(lambda item: item["id"] == "openRecentFile" and item["enabled"] == True, submenu_recent_items))
        folders = list(filter(lambda item: item["id"] == "openRecentFolder" and item["enabled"] == True, submenu_recent_items))
        extract_path = lambda item: item["uri"]["path"]
        files_paths = list(map(extract_path, files))
        folders_paths = list(map(extract_path, folders))

        workspaces_paths = []
        if "profileAssociations" in storage and "workspaces" in storage["profileAssociations"]:
            workspaces = storage["profileAssociations"]["workspaces"]
            workspaces_paths = [path.replace('file://', '') for path in workspaces.keys()]

        return files_paths, folders_paths, workspaces_paths

    # Return favorite projects
    def get_favorite_projects(self) -> List[dict]:
        try:
            projects_path = self.VSCODE_PROJECTS_PATH
            if not projects_path.exists():
                return []

            with open(projects_path, 'r') as f:
                projects = json.load(f)

            if not self.extract_worktrees:
                return projects

            # Process git worktrees for each project
            expanded_projects = []
            for project in projects:
                project_enabled = project.get('enabled', True)
                if not project_enabled:
                    continue

                project_path = Path(project.get('rootPath', ''))
                git_dir = project_path / '.git'

                # If project has .git, check for worktrees
                if git_dir.exists():
                    try:
                        # Get all worktrees
                        worktrees_output = subprocess.check_output(
                            [self.git_executable, 'worktree', 'list'],
                            cwd=project_path,
                            text=True
                        ).splitlines()

                        # Process each worktree
                        for line in worktrees_output:
                            if not line.strip():
                                continue
                            parts = line.split()
                            if len(parts) >= 3:
                                wt_path = parts[0]
                                wt_branch = parts[2].strip('[]')
                                # Create a copy of the project for each worktree
                                wt_project = project.copy()
                                wt_project['rootPath'] = wt_path
                                wt_project['name'] = f"{project['name']}:{wt_branch}"
                                expanded_projects.append(wt_project)
                    except (subprocess.CalledProcessError, OSError) as e:
                        warning(f"Error processing git worktrees for {project_path}: {str(e)}")
                        expanded_projects.append(project)  # Add original project on error
                else:
                    expanded_projects.append(project)  # Add non-git projects as is

            return expanded_projects
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
    def make_recent_item(self, path: str | Path, recent_type: Literal["File", "Folder"]) -> Item:
        resized_path = self.resize_path(path)
        path_splits = resized_path.split("/")
        working_dir_path, filename = path_splits[:-1], path_splits[-1]
        formatted_path = "{}/{}".format("/".join(working_dir_path), filename)

        uri_flag = "--file-uri" if recent_type == "File" else "--folder-uri"
        return self.make_item(
            "{}: {}".format(recent_type, path_splits[-1]), formatted_path,
            [Action(id=path, text="Open in Visual Studio Code",
                    callable=lambda: runDetachedProcess(cmdln=[self.EXECUTABLE, uri_flag, Path(path).as_uri()]))]
        )

    # Return a recent item.
    def make_project_item(self, path: str, name: str) -> Item:
        resized_path = self.resize_path(path)
        path_splits = resized_path.split("/")
        working_dir_path, filename = path_splits[:-1], path_splits[-1]
        formatted_path = "{}/{}".format("/".join(working_dir_path), filename)

        return StandardItem(
            id=md_id, iconUrls=self.ICON_PROJECT, text=name, subtext=formatted_path,
            actions=[Action(id=path, text="Open in Visual Studio Code",
                            callable=lambda: runDetachedProcess(cmdln=[self.EXECUTABLE, '--folder-uri', path]))]
        )

    def handleTriggerQuery(self, query) -> Optional[List[Item]]:
        if not self.EXECUTABLE:
            return query.add(self.make_item("Visual Studio Code not installed"))

        query_text = query.string

        debug("query: '{}'".format(query_text))

        query_text = query_text.strip().lower()
        files, folders, workspaces = self.get_visual_studio_code_recent()
        projects = self.get_favorite_projects()

        debug("vs recent files: {}".format(files))
        debug("vs recent folders: {}".format(folders))
        debug("vs recent workspaces: {}".format(workspaces))

        items = []
        if query_text in "New Empty Window".lower():
            items.append(query.add(self.make_new_window_item()))

        for project in projects:
            project_name = project.get('name', '')
            project_path = project.get('rootPath', '')
            project_enabled = project.get('enabled', True)
            project_tags = project.get('tags', [])

            if not project_enabled or not project_name or not project_path:
                continue

            query_name = query_text
            for tag in project_tags:
                if tag.lower() in query_name:
                    query_name = query_name.replace(tag.lower(), '', 1).strip()

            if query_name not in project_name.lower():
                continue

            if not project_path.startswith(('vscode:', 'file:')):
                project_path = f"file://{project_path}"

            if project_path.startswith(('file:')):
                fs_path = Path(project_path.replace('file://', '', 1))
                if not fs_path.exists():
                    continue

            item = self.make_project_item(project_path, project_name)
            items.append(query.add(item))

        if not folders and not files and not workspaces:
            items.append(query.add(self.make_item("Recent Files and Folders not found")))
            return items

        recent_items = []
        if 'folder' in query_text:
            query_path = query_text.replace('folder', '', 1).strip()
            recent_items = list(dict.fromkeys(folders + workspaces))
        elif 'file' in query_text:
            query_path = query_text.replace('file', '', 1).strip()
            recent_items = files
        else:
            query_path = query_text
            recent_items = list(dict.fromkeys(folders + workspaces)) + files

        for item_path in recent_items:
            if query_path not in item_path.lower() or not Path(item_path).exists():
                continue
            else:
                item_type = "Folder" if item_path in folders or item_path in workspaces else "File"
                item = query.add(self.make_recent_item(item_path, item_type))
            items.append(item)

        return items
