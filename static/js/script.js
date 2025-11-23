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
        }

        // Single download
        async function downloadSingle() {
            const url = document.getElementById('single-url').value.trim();
            const format = document.getElementById('single-format').value;
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
                    body: JSON.stringify({ url, format })
                });
                
                if (!response.ok) {
                    const result = await response.json();
                    showStatus(statusDiv, `❌ ${result.message || 'Download failed'}`, 'error');
                    return;
                }
                
                // Get filename from Content-Disposition header
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'download.zip';
                if (contentDisposition) {
                    const matches = /filename[^;=\n]*=(['"]?)([^'"\n]*?)\1/.exec(contentDisposition);
                    if (matches && matches[2]) {
                        filename = matches[2];
                    }
                }
                
                // Download the file
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(downloadUrl);
                
                showStatus(statusDiv, '✅ Download started!', 'success');
                document.getElementById('single-url').value = '';
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
            const format = document.getElementById('bulk-format').value;
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
                    body: JSON.stringify({ urls, format })
                });
                
                if (!response.ok) {
                    const result = await response.json();
                    showStatus(statusDiv, `❌ ${result.message || 'Bulk download failed'}`, 'error');
                    return;
                }
                
                // Get filename from Content-Disposition header
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'bakraload_bulk_download.zip';
                if (contentDisposition) {
                    const matches = /filename[^;=\n]*=(['"]?)([^'"\n]*?)\1/.exec(contentDisposition);
                    if (matches && matches[2]) {
                        filename = matches[2];
                    }
                }
                
                // Download the file
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(downloadUrl);
                
                showStatus(statusDiv, `✅ Bulk download started! (${urls.length} URLs processed)`, 'success');
                document.getElementById('bulk-urls').value = '';
            } catch (error) {
                showStatus(statusDiv, `❌ Network error: ${error.message}`, 'error');
            } finally {
                spinner.style.display = 'none';
                buttonText.textContent = 'Download All';
                button.disabled = false;
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