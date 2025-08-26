 // Tab switching
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'downloads') {
                refreshDownloads();
            }
        }

        // Single download
        async function downloadSingle() {
            const url = document.getElementById('single-url').value.trim();
            const statusDiv = document.getElementById('single-status');
            const spinner = document.getElementById('single-spinner');
            const buttonText = document.getElementById('single-text');
            const button = document.querySelector('#single-tab .btn');
            
            if (!url) {
                showStatus(statusDiv, 'Please enter a valid URL', 'error');
                return;
            }
            
            // Loading state
            spinner.style.display = 'block';
            buttonText.textContent = 'Downloading...';
            button.disabled = true;
            
            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    let message = `✅ ${result.message}`;
                    if (result.title) message += `\n📝 ${result.title}`;
                    if (result.platform) message += `\n🌐 ${result.platform}`;
                    
                    showStatus(statusDiv, message, 'success');
                    document.getElementById('single-url').value = '';
                } else {
                    showStatus(statusDiv, `❌ ${result.message}`, 'error');
                }
            } catch (error) {
                showStatus(statusDiv, `❌ Network error: ${error.message}`, 'error');
            } finally {
                spinner.style.display = 'none';
                buttonText.textContent = 'Download';
                button.disabled = false;
            }
        }

        // Bulk download
        async function downloadBulk() {
            const urlsText = document.getElementById('bulk-urls').value.trim();
            const statusDiv = document.getElementById('bulk-status');
            const spinner = document.getElementById('bulk-spinner');
            const buttonText = document.getElementById('bulk-text');
            const button = document.querySelector('#bulk-tab .btn');
            
            if (!urlsText) {
                showStatus(statusDiv, 'Please enter at least one URL', 'error');
                return;
            }
            
            const urls = urlsText.split('\n').filter(url => url.trim());
            
            if (urls.length === 0) {
                showStatus(statusDiv, 'Please enter valid URLs', 'error');
                return;
            }
            
            // Loading state
            spinner.style.display = 'block';
            buttonText.textContent = `Processing ${urls.length} URLs...`;
            button.disabled = true;
            
            try {
                const response = await fetch('/bulk-download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ urls })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    let message = `✅ ${result.message}\n\n`;
                    result.results.forEach((res, index) => {
                        const icon = res.status === 'success' ? '✅' : '❌';
                        message += `${icon} URL ${index + 1}: ${res.message}\n`;
                    });
                    
                    showStatus(statusDiv, message, 'success');
                    document.getElementById('bulk-urls').value = '';
                } else {
                    showStatus(statusDiv, `❌ ${result.message}`, 'error');
                }
            } catch (error) {
                showStatus(statusDiv, `❌ Network error: ${error.message}`, 'error');
            } finally {
                spinner.style.display = 'none';
                buttonText.textContent = 'Download All';
                button.disabled = false;
            }
        }

        // Refresh downloads
        async function refreshDownloads() {
            const downloadsDiv = document.getElementById('downloads-list');
            
            try {
                const response = await fetch('/downloads');
                const result = await response.json();
                
                if (result.items && result.items.length > 0) {
                    let html = '<div class="downloads-grid">';
                    
                    result.items.forEach(item => {
                        const isFile = item.type === 'file';
                        const icon = isFile ? '📄' : '📁';
                        const size = isFile ? formatFileSize(item.size) : `${item.file_count} files`;
                        
                        html += `
                            <div class="download-item">
                                <h3 class="download-title">${item.name}</h3>
                                <p class="download-meta">${icon} ${size}</p>
                                <div class="download-actions">
                                    <button class="btn btn-small" onclick="${isFile ? `downloadFile('${item.name}')` : `downloadFolder('${item.name}')`}">
                                        ${isFile ? '⬇️ Download' : '📦 Download ZIP'}
                                    </button>
                                </div>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    downloadsDiv.innerHTML = html;
                } else {
                    downloadsDiv.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">📁</div>
                            <p>No downloads yet. Start downloading some content!</p>
                        </div>
                    `;
                }
            } catch (error) {
                downloadsDiv.innerHTML = `<div class="status status-error">Error loading downloads: ${error.message}</div>`;
            }
        }

        // Download handlers
        function downloadFile(filename) {
            window.open(`/download-file/${encodeURIComponent(filename)}`, '_blank');
        }

        function downloadFolder(foldername) {
            window.open(`/download-folder/${encodeURIComponent(foldername)}`, '_blank');
        }

        // Clear downloads
        async function clearDownloads() {
            if (!confirm('Are you sure you want to clear all downloads?')) return;
            
            try {
                const response = await fetch('/clear-downloads', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    alert('✅ All downloads cleared successfully!');
                    refreshDownloads();
                } else {
                    alert(`❌ Error: ${result.message}`);
                }
            } catch (error) {
                alert(`❌ Network error: ${error.message}`);
            }
        }

        // Utility functions
        function showStatus(container, message, type, append = false) {
            const statusHtml = `<div class="status status-${type}">${message.replace(/\n/g, '<br>')}</div>`;
            
            if (append) {
                container.innerHTML += statusHtml;
            } else {
                container.innerHTML = statusHtml;
            }
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        // Event listeners
        document.getElementById('single-url').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') downloadSingle();
        });

        // Platform detection
        document.getElementById('single-url').addEventListener('input', function(e) {
            const url = e.target.value.toLowerCase();
            const platforms = {
                'youtube.com': 'YouTube', 'youtu.be': 'YouTube',
                'instagram.com': 'Instagram', 'tiktok.com': 'TikTok',
                'twitter.com': 'Twitter', 'x.com': 'Twitter',
                'facebook.com': 'Facebook', 'reddit.com': 'Reddit'
            };
            
            const platform = Object.keys(platforms).find(key => url.includes(key));
            
            if (platform && url.trim()) {
                const statusDiv = document.getElementById('single-status');
                showStatus(statusDiv, `🌐 Detected: ${platforms[platform]}`, 'loading');
            }
        });

        // Initialize particles
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            const particleCount = 50;
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                // Set a random vertical start position (0-80% of viewport height)
                particle.style.top = Math.random() * 80 + 'vh';
                // Animation duration
                const duration = Math.random() * 10 + 10;
                particle.style.animationDuration = duration + 's';
                // Negative animation delay so animation starts in progress
                particle.style.animationDelay = (-Math.random() * duration) + 's';
                particlesContainer.appendChild(particle);
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            createParticles();
            console.log('🚀 Modern Social Media Downloader loaded!');
        });

        console.log('🚀 Modern Social Media Downloader loaded!');

         // Existing script remains unchanged
    document.addEventListener('DOMContentLoaded', function () {
        createParticles();
        console.log('🚀 Modern Social Media Downloader loaded!');
    });