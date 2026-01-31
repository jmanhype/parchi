/**
 * Files Panel Module
 * Handles file storage, display, and management for parchi
 */

import * as fileStorage from '../services/file-storage.js';
import { SidePanelUI } from './panel-ui.js';

/**
 * Setup file panel event listeners
 */
(SidePanelUI.prototype as any).setupFilePanelListeners = function setupFilePanelListeners(this: SidePanelUI) {
  const { dropZone, filesFileInput, selectFilesBtn, clearAllBtn } = this.elements;

  // File input change
  filesFileInput?.addEventListener('change', async (e) => {
    const target = e.target as HTMLInputElement;
    const files = target.files;
    if (files) {
      await handleFiles.call(this, Array.from(files));
      target.value = ''; // Reset input
    }
  });

  // Select files button
  selectFilesBtn?.addEventListener('click', () => {
    filesFileInput?.click();
  });

  // Drag and drop
  dropZone?.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  });

  dropZone?.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
  });

  dropZone?.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = Array.from(e.dataTransfer?.files || []) as File[];
    await handleFiles.call(this, files);
  });

  // Clear all button
  clearAllBtn?.addEventListener('click', async () => {
    if (confirm('Are you sure you want to remove all files?')) {
      await fileStorage.clearAllFiles();
      (this as any).loadFileList();
    }
  });

  // Listen for custom event to refresh list
  const filesPanel = document.getElementById('filesPanel');
  filesPanel?.addEventListener('loadFileList', () => {
    (this as any).loadFileList();
  });
};

/**
 * Handle file selection/upload
 */
async function handleFiles(this: SidePanelUI, files: File[]) {
  for (const file of files) {
    try {
      await fileStorage.storeFile(file);
      console.log('[Files] Stored file:', file.name, fileStorage.formatBytes(file.size));
    } catch (error) {
      console.error('[Files] Failed to store file:', file.name, error);
      alert(`Failed to store ${file.name}: ${error}`);
    }
  }

  // Refresh the file list
  (this as any).loadFileList();
}

/**
 * Load and display the file list
 */
(SidePanelUI.prototype as any).loadFileList = function loadFileList(this: SidePanelUI) {
  renderFileList.call(this);
};

/**
 * Render the file list in the UI
 */
async function renderFileList(this: SidePanelUI) {
  const { fileList, fileListContainer, emptyState, storageUsed } = this.elements;

  if (!fileList) return;

  try {
    const files = await fileStorage.listFiles();
    const totalSize = await fileStorage.getStorageSize();

    // Update storage usage display
    if (storageUsed) {
      storageUsed.textContent = fileStorage.formatBytes(totalSize);
    }

    // Show/hide empty state
    if (emptyState) {
      emptyState.style.display = files.length === 0 ? 'block' : 'none';
    }

    // Show/hide file list container
    if (fileListContainer) {
      fileListContainer.style.display = files.length > 0 ? 'block' : 'none';
    }

    // Clear and populate file list
    fileList.innerHTML = '';

    for (const file of files) {
      const fileItem = createFileItem.call(this, file);
      fileList.appendChild(fileItem);
    }
  } catch (error) {
    console.error('[Files] Failed to load file list:', error);
  }
}

/**
 * Create a file item element
 */
function createFileItem(this: SidePanelUI, file: fileStorage.StoredFile): HTMLElement {
  const item = document.createElement('div');
  item.className = 'file-item';
  item.dataset.fileId = file.id;

  // Get file type icon class
  const iconClass = getFileIconClass(file.type);

  item.innerHTML = `
    <div class="file-icon ${iconClass}"></div>
    <div class="file-info">
      <div class="file-name" title="${file.name}">${file.name}</div>
      <div class="file-meta">${fileStorage.formatBytes(file.size)}</div>
    </div>
    <button class="file-remove" title="Remove file" data-file-id="${file.id}">×</button>
  `;

  // Add remove button handler
  const removeBtn = item.querySelector('.file-remove') as HTMLButtonElement;
  removeBtn?.addEventListener('click', async () => {
    await fileStorage.deleteFile(file.id);
    // Refresh the list
    (this as any).loadFileList();
  });

  return item;
}

/**
 * Get file icon class based on MIME type
 */
function getFileIconClass(mimeType: string): string {
  if (mimeType.startsWith('image/')) return 'file-icon-image';
  if (mimeType.startsWith('video/')) return 'file-icon-video';
  if (mimeType.startsWith('audio/')) return 'file-icon-audio';
  if (mimeType.includes('pdf') || mimeType.includes('document')) return 'file-icon-document';
  if (mimeType.includes('zip') || mimeType.includes('archive') || mimeType.includes('tar')) return 'file-icon-archive';
  return 'file-icon-default';
}
