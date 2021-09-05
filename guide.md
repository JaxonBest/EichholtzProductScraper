# How to use this program.


<article>Let's learn the customize file.</article>


<br/>
<h4>Step #1. Open the customize.txt file that came with the program</h4>
<br/>


<h4>Step #2. Try out your first command<h4>


<strong>It is important to note that any line you write with a "#" before it will not be read by the program!</strong> 


<br/>


p>Type in the following command: </p>


```
EXPORT_TO_EXCEL yes
```


<article>A lot of preferences can be turned on and off with yes/no.</article>


<br/>


<h4>Step #3. Save the file and you're good to go.</h4>


<br/>


<h4>Step #4 (Optional). Take a short read through the all of the possible commands below</h4>


<article>**The keyword means what response it takes in for example. My command -> [EXPORT_TO_EXCEL **yes**]</article>


<article>In that case **yes** would be the keyword.</article>


```

EXPORT_TO_EXCEL | Keywords (yes, no) | Default (yes)

EXPORT_INTO_SUBDIR | Keywords (yes, no) | Default (yes) | This is a simple organization command meaning it will create a folder for each item. Otherwise can be messy.

MULTI_THREAD_IMG_DOWNLOAD | Keywords (yes, no) | Default (true) | Using this will rapidly download all the product images. But downside is it's a little dangerous for multi-page

DISABLE_USER_AGENT | Keywords (yes, no) | Default(no) | User-agents will spoof your web browser allowing a safer data transfer. Probably not the best idea to disable it.

DO_EXPORT | Keywords (yes, no) | Default(yes) | All the output is already in the terminal, so if you don't want to generate an output. It's optional.

USE_EXCEL_LABELING | keywords (yes, no) | Default(yes) | Labels each field like sku, name, url etc. It requires you to have EXPORT_TO_EXCEL enabled.
```