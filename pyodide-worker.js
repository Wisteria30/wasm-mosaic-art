// pyodide-worker.js
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js";

importScripts(PYODIDE_URL);

async function initializePyodide() {
    self.pyodide = await loadPyodide({
        indexURL: PYODIDE_URL.split('/').slice(0, -1).join('/'),
    });
    await self.pyodide.loadPackage(["numpy", "pillow"]);
    
    // Pythonスクリプトを外部ファイルから読み込む
    const response = await fetch('mosaic.py');
    const pythonScript = await response.text();
    
    // 読み込んだPythonスクリプトを実行
    self.pyodide.runPython(pythonScript);

    self.postMessage({status: 'initialized'});
}

let pyodideReadyPromise = initializePyodide();

self.onmessage = async function(e) {
    await pyodideReadyPromise;
    
    if (e.data.command === 'process') {
        const imageData = e.data.imageData;
        const result = self.pyodide.runPython(`create_mosaic('${imageData}')`);
        self.postMessage({status: 'done', result: result});
    }
};
