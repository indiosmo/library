"use strict";

const obsidian = require("obsidian");

const VIDEO_EXTENSIONS = new Set([
    "webm",
    "mp4",
    "mov",
    "mkv",
    "ogv",
    "avi",
    "m4v",
]);
const INFO_SUFFIX = ".info.json";
const TIMESTAMP_REGEX = /\b(\d{1,2}:\d{2}(?::\d{2})?)\b/g;
const SKIP_PARENT_SELECTOR = "code, pre, a, .video-timestamp";
const MEDIA_FRONTMATTER_KEYS = new Set(["file", "media"]);
const TOOLBAR_CLASS = "video-toolbar";
const VIDEO_WAIT_ATTEMPTS = 40;
const VIDEO_WAIT_INTERVAL_MS = 50;

function isMediaKey(key) {
    return (
        MEDIA_FRONTMATTER_KEYS.has(key) ||
        Array.from(MEDIA_FRONTMATTER_KEYS).some((prefix) =>
            key.startsWith(`${prefix}.`) || key.startsWith(`${prefix}[`),
        )
    );
}

function parseTimestamp(text) {
    const parts = text.split(":").map((part) => Number.parseInt(part, 10));
    if (parts.some(Number.isNaN)) return null;
    if (parts.length === 2) return parts[0] * 60 + parts[1];
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
    return null;
}

function formatTimestamp(seconds) {
    const total = Math.max(0, Math.floor(seconds));
    const hours = Math.floor(total / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const secs = total % 60;
    const pad = (value) => value.toString().padStart(2, "0");
    if (hours > 0) return `${hours}:${pad(minutes)}:${pad(secs)}`;
    return `${minutes}:${pad(secs)}`;
}

class VideoTimestampsPlugin extends obsidian.Plugin {
    async onload() {
        this.registerMarkdownPostProcessor((element, context) => {
            const video = this.findVideoForNote(context.sourcePath);
            if (!video) return;
            this.decorateElement(element, video);
        });

        const refresh = () => this.refreshToolbars();
        this.registerEvent(this.app.workspace.on("layout-change", refresh));
        this.registerEvent(this.app.workspace.on("file-open", refresh));
        this.app.workspace.onLayoutReady(refresh);
    }

    onunload() {
        this.app.workspace.iterateAllLeaves((leaf) => {
            const containerEl = leaf.view && leaf.view.containerEl;
            if (!containerEl) return;
            for (const toolbar of containerEl.querySelectorAll(`.${TOOLBAR_CLASS}`)) {
                if (toolbar._abortController) toolbar._abortController.abort();
                toolbar.remove();
            }
        });
    }

    refreshToolbars() {
        this.app.workspace.iterateAllLeaves((leaf) => {
            const view = leaf.view;
            if (!view || !view.file) return;
            const extension =
                view.file.extension && view.file.extension.toLowerCase();
            if (!VIDEO_EXTENSIONS.has(extension)) return;
            this.ensureToolbar(leaf, view.file);
        });
    }

    async ensureToolbar(leaf, videoFile) {
        const videoElement = await this.waitForVideoElement(leaf);
        if (!videoElement) return;
        const container = videoElement.parentElement;
        if (!container) return;

        const existing = container.querySelector(`:scope > .${TOOLBAR_CLASS}`);
        if (
            existing &&
            existing.dataset.videoPath === videoFile.path &&
            existing._videoElement === videoElement
        ) {
            return;
        }
        if (existing) {
            if (existing._abortController) existing._abortController.abort();
            existing.remove();
        }

        const placeholder = document.createElement("div");
        placeholder.className = TOOLBAR_CLASS;
        placeholder.dataset.videoPath = videoFile.path;
        placeholder._videoElement = videoElement;
        container.insertBefore(placeholder, videoElement.nextSibling);

        const abortController = new AbortController();
        const toolbar = await this.buildToolbar(
            videoFile,
            videoElement,
            abortController.signal,
        );
        if (!placeholder.isConnected) {
            abortController.abort();
            return;
        }
        if (!toolbar) {
            placeholder.remove();
            abortController.abort();
            return;
        }
        toolbar._abortController = abortController;
        toolbar._videoElement = videoElement;
        container.replaceChild(toolbar, placeholder);
    }

    async buildToolbar(videoFile, videoElement, signal) {
        const chapters = await this.loadChapters(videoFile);
        if (chapters.length === 0) return null;

        const toolbar = document.createElement("div");
        toolbar.className = TOOLBAR_CLASS;
        toolbar.dataset.videoPath = videoFile.path;
        toolbar.appendChild(this.buildChapterList(videoElement, chapters, signal));
        return toolbar;
    }

    buildChapterList(videoElement, chapters, signal) {
        const wrapper = document.createElement("div");
        wrapper.className = "video-toolbar-row video-toolbar-chapters";

        const heading = document.createElement("div");
        heading.className = "video-toolbar-heading";
        heading.textContent = "Chapters";
        wrapper.appendChild(heading);

        const list = document.createElement("ol");
        list.className = "video-chapter-list";

        const items = [];
        for (let index = 0; index < chapters.length; index++) {
            const chapter = chapters[index];
            const item = document.createElement("li");
            item.className = "video-chapter-item";
            item.dataset.start = String(chapter.start);

            const link = document.createElement("a");
            link.href = "#";
            link.className = "video-chapter-link";

            const time = document.createElement("span");
            time.className = "video-chapter-time";
            time.textContent = formatTimestamp(chapter.start);

            const title = document.createElement("span");
            title.className = "video-chapter-title";
            title.textContent = chapter.title;

            link.append(time, title);
            link.addEventListener(
                "click",
                (event) => {
                    event.preventDefault();
                    videoElement.currentTime = chapter.start;
                    videoElement.play().catch(() => {});
                },
                { signal },
            );

            item.appendChild(link);
            list.appendChild(item);
            items.push(item);
        }

        wrapper.appendChild(list);

        const updateActive = () => {
            const time = videoElement.currentTime;
            let activeIndex = -1;
            for (let index = 0; index < chapters.length; index++) {
                if (chapters[index].start <= time) activeIndex = index;
                else break;
            }
            for (let index = 0; index < items.length; index++) {
                items[index].classList.toggle("is-active", index === activeIndex);
            }
        };

        videoElement.addEventListener("timeupdate", updateActive, { signal });
        videoElement.addEventListener("seeked", updateActive, { signal });
        updateActive();

        return wrapper;
    }

    async loadChapters(videoFile) {
        const infoChapters = await this.loadInfoChapters(videoFile);
        if (infoChapters.length > 0) return infoChapters;
        return this.loadArticleChapters(videoFile);
    }

    async loadInfoChapters(videoFile) {
        const folder = videoFile.parent;
        if (!folder) return [];
        const targetName = `${videoFile.basename}${INFO_SUFFIX}`;
        const infoFile = folder.children.find(
            (child) => child instanceof obsidian.TFile && child.name === targetName,
        );
        if (!infoFile) return [];
        try {
            const text = await this.app.vault.read(infoFile);
            const info = JSON.parse(text);
            const chapters = info.chapters;
            if (!Array.isArray(chapters)) return [];
            return chapters
                .filter((chapter) => typeof chapter.start_time === "number")
                .map((chapter) => ({
                    start: chapter.start_time,
                    title: (chapter.title || "").trim(),
                }));
        } catch {
            return [];
        }
    }

    async loadArticleChapters(videoFile) {
        const note = this.findNoteForVideo(videoFile);
        if (!note) return [];
        try {
            const text = await this.app.vault.read(note);
            return this.parseMarkdownChapters(text);
        } catch {
            return [];
        }
    }

    findNoteForVideo(videoFile) {
        const markdownFiles = this.app.vault.getMarkdownFiles();
        for (const file of markdownFiles) {
            const cache = this.app.metadataCache.getFileCache(file);
            if (!cache) continue;
            const mediaLinks = (cache.frontmatterLinks || []).filter((reference) =>
                isMediaKey(reference.key),
            );
            for (const reference of mediaLinks) {
                const target = this.app.metadataCache.getFirstLinkpathDest(
                    reference.link,
                    file.path,
                );
                if (target && target.path === videoFile.path) return file;
            }
        }
        return null;
    }

    parseMarkdownChapters(text) {
        const lines = text.split(/\r?\n/);
        const chapters = [];
        let inChapters = false;
        for (const line of lines) {
            if (!inChapters) {
                if (/^#{1,6}\s+Chapters\s*$/i.test(line.trim())) {
                    inChapters = true;
                }
                continue;
            }
            if (/^#{1,6}\s+\S/.test(line)) break;

            const chapter = this.parseMarkdownChapterLine(line);
            if (chapter) chapters.push(chapter);
        }
        return chapters;
    }

    parseMarkdownChapterLine(line) {
        const match = line.match(
            /^\s*(?:[-*+]\s+)?(\d{1,2}:\d{2}(?::\d{2})?)\s*(?:[-\u2013\u2014:]\s*)?(.*\S)\s*$/,
        );
        if (!match) return null;
        const start = parseTimestamp(match[1]);
        if (start === null) return null;
        return {
            start,
            title: match[2].trim(),
        };
    }

    async waitForVideoElement(leaf) {
        for (let attempt = 0; attempt < VIDEO_WAIT_ATTEMPTS; attempt++) {
            const containerEl = leaf.view && leaf.view.containerEl;
            const element = containerEl && containerEl.querySelector("video");
            if (element) return element;
            await new Promise((resolve) =>
                setTimeout(resolve, VIDEO_WAIT_INTERVAL_MS),
            );
        }
        return null;
    }

    decorateElement(element, video) {
        const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, {
            acceptNode: (node) => {
                const parent = node.parentElement;
                if (!parent) return NodeFilter.FILTER_REJECT;
                if (parent.closest(SKIP_PARENT_SELECTOR)) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            },
        });
        const textNodes = [];
        let node;
        while ((node = walker.nextNode())) textNodes.push(node);
        for (const textNode of textNodes) this.wrapTimestamps(textNode, video);
    }

    wrapTimestamps(textNode, video) {
        const text = textNode.textContent;
        TIMESTAMP_REGEX.lastIndex = 0;
        const fragment = document.createDocumentFragment();
        let cursor = 0;
        let matched = false;
        let match;
        while ((match = TIMESTAMP_REGEX.exec(text)) !== null) {
            const seconds = parseTimestamp(match[1]);
            if (seconds === null) continue;
            matched = true;
            if (match.index > cursor) {
                fragment.appendChild(
                    document.createTextNode(text.slice(cursor, match.index)),
                );
            }
            fragment.appendChild(this.createTimestampLink(match[1], seconds, video));
            cursor = match.index + match[1].length;
        }
        if (!matched) return;
        if (cursor < text.length) {
            fragment.appendChild(document.createTextNode(text.slice(cursor)));
        }
        textNode.parentNode.replaceChild(fragment, textNode);
    }

    createTimestampLink(text, seconds, video) {
        const link = document.createElement("a");
        link.className = "video-timestamp";
        link.textContent = text;
        link.href = "#";
        link.title = `Jump to ${text} in ${video.basename}`;
        link.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            this.jumpTo(video, seconds);
        });
        return link;
    }

    findVideoForNote(sourcePath) {
        const file = this.app.vault.getAbstractFileByPath(sourcePath);
        if (!file) return null;
        const cache = this.app.metadataCache.getFileCache(file);
        if (!cache) return null;
        const mediaLinks = (cache.frontmatterLinks || []).filter((reference) =>
            isMediaKey(reference.key),
        );
        for (const reference of mediaLinks) {
            const target = this.app.metadataCache.getFirstLinkpathDest(
                reference.link,
                sourcePath,
            );
            if (target && VIDEO_EXTENSIONS.has(target.extension.toLowerCase())) {
                return target;
            }
        }
        return null;
    }

    async jumpTo(video, seconds) {
        let targetLeaf = null;
        this.app.workspace.iterateAllLeaves((leaf) => {
            const view = leaf.view;
            if (view && view.file && view.file.path === video.path) {
                targetLeaf = leaf;
            }
        });
        if (!targetLeaf) {
            targetLeaf = this.app.workspace.getLeaf("split");
            await targetLeaf.openFile(video);
        } else {
            this.app.workspace.revealLeaf(targetLeaf);
        }
        await this.seekVideo(targetLeaf, seconds);
    }

    async seekVideo(leaf, seconds) {
        const videoElement = await this.waitForVideoElement(leaf);
        if (!videoElement) {
            new obsidian.Notice("Video element not found");
            return;
        }
        const apply = () => {
            videoElement.currentTime = seconds;
            videoElement.play().catch(() => {});
        };
        if (videoElement.readyState >= 1) {
            apply();
        } else {
            videoElement.addEventListener("loadedmetadata", apply, { once: true });
        }
    }
}

module.exports = VideoTimestampsPlugin;
