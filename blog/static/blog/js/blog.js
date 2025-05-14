/**
 * ML DEVLOG - Blog JavaScript
 * Enhanced syntax highlighter with multiple language support
 */

document.addEventListener('DOMContentLoaded', function() {
    // Enhanced syntax highlighter function
    function highlightSyntax() {
        const codeBlocks = document.querySelectorAll('pre code');
        
        codeBlocks.forEach(block => {
            // Get the language class
            const languageClass = Array.from(block.classList).find(cls => cls.startsWith('language-'));
            const language = languageClass ? languageClass.replace('language-', '') : 'plaintext';
            
            // Get the code text
            const code = block.textContent;
            
            // Apply syntax highlighting based on language
            let highlightedCode = code;
            
            switch (language) {
                case 'python':
                    highlightedCode = highlightPython(code);
                    break;
                case 'javascript':
                    highlightedCode = highlightJavaScript(code);
                    break;
                case 'html':
                    highlightedCode = highlightHTML(code);
                    break;
                case 'css':
                    highlightedCode = highlightCSS(code);
                    break;
                case 'terminal':
                    highlightedCode = highlightTerminal(code);
                    break;
                case 'markdown':
                    highlightedCode = highlightMarkdown(code);
                    break;
                case 'json':
                    highlightedCode = highlightJSON(code);
                    break;
                case 'sql':
                    highlightedCode = highlightSQL(code);
                    break;
                case 'bash':
                    highlightedCode = highlightBash(code);
                    break;
                default:
                    // For plaintext, just keep as is
                    break;
            }
            
            // Update code block with highlighted code
            block.innerHTML = highlightedCode;
        });
    }
    
    // Python syntax highlighting
    function highlightPython(code) {
        const patterns = [
            { pattern: /\b(def|class|import|from|as|return|if|else|elif|for|while|try|except|finally|with|in|is|not|and|or|True|False|None)\b/g, class: 'keyword' },
            { pattern: /\b([A-Za-z_][A-Za-z0-9_]*)\s*\(/g, class: 'function' },
            { pattern: /(["'])(.*?)\1/g, class: 'string' },
            { pattern: /#.*$/gm, class: 'comment' },
            { pattern: /\b([A-Z][A-Za-z0-9_]*)\b/g, class: 'class' },
            { pattern: /\b(\d+(\.\d+)?)\b/g, class: 'number' },
            { pattern: /(\+|\-|\*|\/|\%|\=|\<|\>|\!|\||\&|\^|\~|\:)/g, class: 'operator' },
            { pattern: /\b(print|len|str|int|float|list|dict|set|tuple|range|enumerate|zip|map|filter|sorted|sum|min|max)\b/g, class: 'builtin' }
        ];
        
        return applyPatterns(code, patterns);
    }
    
    // JavaScript syntax highlighting
    function highlightJavaScript(code) {
        const patterns = [
            { pattern: /\b(var|let|const|function|return|if|else|for|while|do|switch|case|break|continue|try|catch|finally|new|this|class|extends|import|export|default|null|undefined|true|false)\b/g, class: 'keyword' },
            { pattern: /\b([A-Za-z_$][A-Za-z0-9_$]*)\s*\(/g, class: 'function' },
            { pattern: /(["'`])(.*?)\1/g, class: 'string' },
            { pattern: /\/\/.*$/gm, class: 'comment' },
            { pattern: /\/\*[\s\S]*?\*\//g, class: 'comment' },
            { pattern: /\b([A-Z][A-Za-z0-9_$]*)\b/g, class: 'class' },
            { pattern: /\b(\d+(\.\d+)?)\b/g, class: 'number' },
            { pattern: /(\+|\-|\*|\/|\%|\=|\<|\>|\!|\||\&|\^|\~|\:|\?|\.)/g, class: 'operator' },
            { pattern: /\b(console|document|window|Array|Object|String|Number|Boolean|Function|RegExp|Math|Date|JSON)\b/g, class: 'builtin' }
        ];
        
        return applyPatterns(code, patterns);
    }
    
    // HTML syntax highlighting
    function highlightHTML(code) {
        const patterns = [
            { pattern: /(&lt;!DOCTYPE.*?&gt;)/g, class: 'doctype' },
            { pattern: /(&lt;)(\/?)([\w-]+)(\s*)(.*?)(\/?&gt;)/g, class: 'tag', processGroups: true },
            { pattern: /(["'])(.*?)\1/g, class: 'string' },
            { pattern: /(&lt;!--)(.*?)(-*&gt;)/g, class: 'comment', processGroups: true },
            { pattern: /(\s+)([\w-]+)(=)/g, class: 'attr-name', processGroups: true }
        ];
        
        // Convert < and > to entities to ensure proper matching
        let processedCode = code.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        
        // Process tag patterns specially
        processedCode = processedCode.replace(/(&lt;)(\/?)([\w-]+)(\s*)(.*?)(\/?&gt;)/g, (match, p1, p2, p3, p4, p5, p6) => {
            return `${p1}${p2}<span class="tag">${p3}</span>${p4}${p5}${p6}`;
        });
        
        // Process attribute names
        processedCode = processedCode.replace(/(\s+)([\w-]+)(=)/g, (match, p1, p2, p3) => {
            return `${p1}<span class="attr-name">${p2}</span>${p3}`;
        });
        
        // Apply other patterns
        const otherPatterns = [
            { pattern: /(["'])(.*?)\1/g, class: 'string' },
            { pattern: /(&lt;!--)(.*?)(-*&gt;)/g, class: 'comment' }
        ];
        
        return applyPatterns(processedCode, otherPatterns);
    }
    
    // CSS syntax highlighting
    function highlightCSS(code) {
        const patterns = [
            { pattern: /([\w-]+)(?=\s*:)/g, class: 'property' },
            { pattern: /(:)([\s\S]*?)(?=;|\}|$)/g, class: 'value', processGroups: true },
            { pattern: /(#[\da-f]{3,8}\b)/gi, class: 'color' },
            { pattern: /(\.)([\w-]+)/g, class: 'class-selector', processGroups: true },
            { pattern: /(\#)([\w-]+)/g, class: 'id-selector', processGroups: true },
            { pattern: /(@[\w-]+)/g, class: 'at-rule' },
            { pattern: /(\/\*[\s\S]*?\*\/)/g, class: 'comment' }
        ];
        
        // Process selectors and values specially
        let processedCode = code.replace(/(:)([\s\S]*?)(?=;|\}|$)/g, (match, p1, p2) => {
            return `${p1}<span class="value">${p2}</span>`;
        });
        
        // Process class and id selectors
        processedCode = processedCode.replace(/(\.)([\w-]+)/g, (match, p1, p2) => {
            return `${p1}<span class="class-selector">${p2}</span>`;
        });
        
        processedCode = processedCode.replace(/(\#)([\w-]+)/g, (match, p1, p2) => {
            return `${p1}<span class="id-selector">${p2}</span>`;
        });
        
        // Apply other patterns
        const otherPatterns = [
            { pattern: /([\w-]+)(?=\s*:)/g, class: 'property' },
            { pattern: /(#[\da-f]{3,8}\b)/gi, class: 'color' },
            { pattern: /(@[\w-]+)/g, class: 'at-rule' },
            { pattern: /(\/\*[\s\S]*?\*\/)/g, class: 'comment' }
        ];
        
        return applyPatterns(processedCode, otherPatterns);
    }
    
    // Terminal syntax highlighting
    function highlightTerminal(code) {
        const patterns = [
            { pattern: /^\$.*/gm, class: 'command' },
            { pattern: /\b(cp|ls|cd|mkdir|rm|mv|touch|cat|grep|echo|sudo|apt|yum|npm|git|python|node)\b/g, class: 'command-name' },
            { pattern: /--(\w+-)*\w+/g, class: 'argument' },
            { pattern: /\b\/([\w\/\.-]+)\b/g, class: 'path' },
            { pattern: /(["'])(.*?)\1/g, class: 'string' },
            { pattern: /#.*$/gm, class: 'comment' }
        ];
        
        return applyPatterns(code, patterns);
    }
    
    // Markdown syntax highlighting
    function highlightMarkdown(code) {
        const patterns = [
            { pattern: /^(#{1,6}\s.*$)/gm, class: 'heading' },
            { pattern: /(\*\*|__)(.*?)\1/g, class: 'bold' },
            { pattern: /(\*|_)(.*?)\1/g, class: 'italic' },
            { pattern: /(!?\[)(.*?)(\]\()(.*?)(\))/g, class: 'link', processGroups: true },
            { pattern: /^(>.*$)/gm, class: 'blockquote' },
            { pattern: /^(\s*[-+*]\s+)/gm, class: 'list-item' },
            { pattern: /^(\s*\d+\.\s+)/gm, class: 'list-item' },
            { pattern: /(`{1,3})(.*?)\1/g, class: 'code', processGroups: true },
            { pattern: /^(```[\s\S]*?```$)/gm, class: 'codeblock' }
        ];
        
        // Process markdown link patterns specially
        let processedCode = code.replace(/(!?\[)(.*?)(\]\()(.*?)(\))/g, (match, p1, p2, p3, p4, p5) => {
            return `${p1}<span class="link-text">${p2}</span>${p3}<span class="link-url">${p4}</span>${p5}`;
        });
        
        // Process code spans
        processedCode = processedCode.replace(/(`{1,3})(.*?)\1/g, (match, p1, p2) => {
            return `${p1}<span class="code-text">${p2}</span>${p1}`;
        });
        
        // Apply other patterns
        const otherPatterns = [
            { pattern: /^(#{1,6}\s.*$)/gm, class: 'heading' },
            { pattern: /(\*\*|__)(.*?)\1/g, class: 'bold' },
            { pattern: /(\*|_)(.*?)\1/g, class: 'italic' },
            { pattern: /^(>.*$)/gm, class: 'blockquote' },
            { pattern: /^(\s*[-+*]\s+)/gm, class: 'list-item' },
            { pattern: /^(\s*\d+\.\s+)/gm, class: 'list-item' },
            { pattern: /^(```[\s\S]*?```$)/gm, class: 'codeblock' }
        ];
        
        return applyPatterns(processedCode, otherPatterns);
    }
    
    // JSON syntax highlighting
    function highlightJSON(code) {
        const patterns = [
            { pattern: /(["'])(.*?)\1(?=\s*:)/g, class: 'property' },
            { pattern: /:\s*(["'])(.*?)\1/g, class: 'string' },
            { pattern: /:\s*(true|false|null)/g, class: 'keyword' },
            { pattern: /:\s*(-?\d+(\.\d+)?([eE][+-]?\d+)?)/g, class: 'number' }
        ];
        
        return applyPatterns(code, patterns);
    }
    
    // SQL syntax highlighting
    function highlightSQL(code) {
        const patterns = [
            { pattern: /\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|AND|OR|JOIN|LEFT|RIGHT|INNER|OUTER|GROUP BY|ORDER BY|HAVING|LIMIT|OFFSET|UNION|CREATE|ALTER|DROP|TABLE|INDEX|VIEW|TRIGGER|PROCEDURE|FUNCTION|AS|IN|BETWEEN|LIKE|IS|NULL|NOT|DISTINCT|COUNT|SUM|AVG|MIN|MAX)\b/gi, class: 'keyword' },
            { pattern: /(["'])(.*?)\1/g, class: 'string' },
            { pattern: /\b\d+\b/g, class: 'number' },
            { pattern: /--.*$/gm, class: 'comment' },
            { pattern: /\/\*[\s\S]*?\*\//g, class: 'comment' },
            { pattern: /(\[)(.*?)(\])/g, class: 'identifier', processGroups: true }
        ];
        
        // Process SQL identifier patterns specially
        let processedCode = code.replace(/(\[)(.*?)(\])/g, (match, p1, p2, p3) => {
            return `${p1}<span class="identifier">${p2}</span>${p3}`;
        });
        
        return applyPatterns(processedCode, patterns);
    }
    
    // Bash/Shell syntax highlighting
    function highlightBash(code) {
        const patterns = [
            { pattern: /^\$.*/gm, class: 'prompt' },
            { pattern: /\b(if|then|else|elif|fi|case|esac|for|while|until|do|done|in|function|time|export|declare|local|readonly|return|exit|set|unset|shift)\b/g, class: 'keyword' },
            { pattern: /\b(echo|cd|pwd|ls|mkdir|rm|cp|mv|cat|grep|find|awk|sed|ssh|scp|curl|wget|apt|yum|dnf|git|make|touch|chmod|chown|man)\b/g, class: 'command' },
            { pattern: /(["'])(.*?)\1/g, class: 'string' },
            { pattern: /#.*$/gm, class: 'comment' },
            { pattern: /\$\{.*?\}/g, class: 'variable' },
            { pattern: /\$\w+/g, class: 'variable' },
            { pattern: /--?\w+/g, class: 'argument' }
        ];
        
        return applyPatterns(code, patterns);
    }
    
    // Helper function to apply patterns
    function applyPatterns(code, patterns) {
        let result = code;
        
        patterns.forEach(({ pattern, class: className, processGroups }) => {
            if (processGroups) {
                // Skip patterns that need special processing
                return;
            }
            
            result = result.replace(pattern, match => {
                // For function patterns, preserve the parenthesis
                if (className === 'function' && pattern.toString().includes('\\(')) {
                    const funcName = match.slice(0, -1);
                    return `<span class="${className}">${funcName}</span>(`;
                }
                return `<span class="${className}">${match}</span>`;
            });
        });
        
        return result;
    }
    
    // Rest of the code from earlier (terminal typing effect, etc.)
    function addTerminalEffect() {
        const featuredCodeBlock = document.querySelector('.featured-post-card .code-content pre code');
        if (featuredCodeBlock) {
            const originalCode = featuredCodeBlock.innerHTML;
            
            // Only apply effect if there's actual code
            if (originalCode && originalCode !== '# No code available') {
                featuredCodeBlock.innerHTML = '';
                
                // Split code into lines
                const codeLines = originalCode.split('\n');
                let lineIndex = 0;
                let charIndex = 0;
                
                // Type out each character
                const typeInterval = setInterval(() => {
                    if (lineIndex < codeLines.length) {
                        const line = codeLines[lineIndex];
                        
                        if (charIndex < line.length) {
                            // Append next character
                            featuredCodeBlock.innerHTML += line[charIndex];
                            charIndex++;
                        } else {
                            // End of line, add newline and move to next line
                            featuredCodeBlock.innerHTML += '\n';
                            lineIndex++;
                            charIndex = 0;
                            
                            // Apply syntax highlighting to the current content
                            highlightSyntax();
                        }
                    } else {
                        // End of code, clear interval
                        clearInterval(typeInterval);
                        
                        // Final highlighting pass
                        highlightSyntax();
                    }
                }, 30); // Adjust typing speed as needed
            } else {
                // If no code, just apply highlighting
                highlightSyntax();
            }
        } else {
            // If not featured code block, just apply highlighting for all code blocks
            highlightSyntax();
        }
    }
    
    // Initialize effects
    highlightSyntax();
    setTimeout(addTerminalEffect, 1000); // Small delay to ensure DOM is ready
    
    // Add copy code functionality
    function addCopyButtons() {
        const codeBlocks = document.querySelectorAll('.code-block');
        
        codeBlocks.forEach(block => {
            const header = block.querySelector('.code-header');
            if (header) {
                const copyButton = document.createElement('button');
                copyButton.className = 'copy-button';
                copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                copyButton.title = 'Copy code';
                copyButton.style.marginLeft = 'auto';
                copyButton.style.background = 'transparent';
                copyButton.style.border = 'none';
                copyButton.style.color = '#808080';
                copyButton.style.cursor = 'pointer';
                copyButton.style.fontSize = '14px';
                
                copyButton.addEventListener('click', () => {
                    const code = block.querySelector('code');
                    if (code) {
                        navigator.clipboard.writeText(code.textContent).then(() => {
                            copyButton.innerHTML = '<i class="fas fa-check"></i>';
                            copyButton.style.color = '#27c93f';
                            
                            setTimeout(() => {
                                copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                                copyButton.style.color = '#808080';
                            }, 2000);
                        });
                    }
                });
                
                header.appendChild(copyButton);
            }
        });
    }
    
    // Add copy functionality after a delay to ensure the DOM is fully loaded
    setTimeout(addCopyButtons, 1500);
});