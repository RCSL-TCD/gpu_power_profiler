# GPU Power Consumption Profiler for visual processing algorithms

## 🖥️ GPU Profiler API

This CLI interface can be invoked from bash to invoke the application whose energy is to be estimated. For developing this tool, we have used NVIDIA NSIFHT COMPUTE  to extract the performance metrics and instruction-level statistics of the task being profiled. The extracted data from the profiler is processed into a required format and subsequently fed as input features for a pre-trained estimator, which then estimates the power consumption based on these low-level CPU metrics.

**Key requirements and notes about the tool are as below:** <br>
● Supported OS: Windows, Linux <br>
● NVIDIA Nsight Compute must be pre-installed. <br>
● You can download it from: https://developer.nvidia.com/cuda-toolkit <br>
● Currently tested on NVIDIA commercial GPUs, but the model could be adapted to any modern GPU based systems. <br>
● Python version 3.x




 ## 💾 Installation  Instructions

The profiling tool is openly made available via the GitHub repository, from which users can download and install the tool using standard git clone and pip install commands. It is expected that the user has installed Intel VTune Profiler from the link given above. 

Creating a virtual environment is highly recommended to prevent dependency conflicts between existing projects and tools, and to safely test the profiling tool. 


<pre> 
```power shell
git clone git@github.com:RCSL-TCD/gpu_power_profiler.git
cd cpu_power_profiler
pip install . 
</pre>




## 📦 File Structure

The resulting file structure should be as shown below.

```
gpu_power_profiler/
├── gpu_profiler/                   # Package containing logic and model files
│   ├── __init__.py
│   ├── cli.py    
│   ├── gpu_profiler.py             # CLI tool entry point
│   ├── gpu_profiler3.py
│   ├── feature_extract.py
│   ├── predict_power.py
│   ├── model_min.joblib
│   ├── model_avg.joblib
│   └── model_max.joblib 
├── setup.py                    # Package installer script
└── MANIFEST.in                 # Includes .joblib files in the package
```


## 🛠️ CLI Options



| Option | Description |
|--------|-------------|
| `-m`   | Specifies which power value to estimate. <br> By default, it estimates the average power consumption of the profiled task. <br>You can specify:<br>• `-m min`<br>• `-m avg`<br>• `-m peak`<br>• `-m all`<br>to estimate the minimum, peak, and average power values. |
| `-a`   | Specifies the application/task’s executable that needs to be profiled.<br>  Provide the **full path** to the application.<br> Example:<br>`python gpu_profiler -a C:\Nuke\Nuke15.0v4\Nuke.exe` |
| `-c`   | Points to a previously generated NVIDIA Nsight Compute `.csv` file for power estimation. <br> Full path to the extracted data should be provided.<br> When this is used, the `-a` switch is ignored.<br>Example:<br>`python gpu_profiler -c /usr/local/Nsight_profiled.csv` |
| `-s`   | Passes argument to the tool under investigation.<br> For e.g., to load Nuke script to be profiled,<br> -s can be used to point to the location of .nk . <br> Example:<br>gpu_profiler -m all -a "c:\Program Files\Nuke15.0v4\Nuke15.0.exe"  -s  "D:/nuke_graphs/blur_image.nk" |










</pre>

The tool allows Three modes for testing <br>
(a) Fully Automated mode <br>
(b)Semi-manual mode <br>

(a) Fully Automated Mode

In the simplest form, both steps are fully automated and handled by the API. The application/task to be profiled is specified using the -a configuration, and the -m switch specifies the estimator(s) that would be invoked post the profiling phase. With Nuke, the below examples open the application in profiling mode (through Vtune), and the specific task graph is loaded manually; however, this can also be automated using command line switches offered by Nuke. <br>

Examples:  

<pre>
gpu_profiler -m min -a "C:\Program Files\Nuke15.0v4\Nuke15.0.exe"   
</pre>

<pre>
gpu_profiler -m avg -a "C:\Program Files\Nuke15.0v4\Nuke15.0.exe"   
</pre>

<pre>
gpu_profiler -m peak -a "C:\Program Files\Nuke15.0v4\Nuke15.0.exe" 
</pre>

<pre>
gpu_profiler -m all  -a "C:\Program Files\Nuke15.0v4\Nuke15.0.exe" 
</pre>

<pre>
gpu_profiler -m all -a "C:\Program Files\Nuke15.0v4\Nuke15.0.exe"  -s  "D:/nuke_graphs/blur_image.nk"
</pre>

Note that the above cases use Windows as the host OS. 

(b) Semi-manual Mode

This option can be exercised if the profiling of the tool has already been completed using VTune and the performance counter values are available in a CSV format. In this case, the -a switch should not be used, and the -c switch can be used to point to the .csv file for energy estimation. If the .csv file is available in the local directory, then the -c switch can also be ignored, as shown in the first example. 

Examples
<pre>
gpu_profiler -m min  
</pre>

<pre>
gpu_profiler -m avg  
</pre>

<pre>
gpu_profiler -m peak
</pre>

<pre>
gpu_profiler -m all -c &lt;path\to\.csv\file.csv&gt;
</pre>













