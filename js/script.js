class SortBox {
	static length = 0;
	static divs = 0;
	static blocklen = 0;
    static duration = 0;
	static canvas = [];
		
	static shufflearr(array) {
		let currentIndex = array.length, temporaryValue, randomIndex;
		while (0 !== currentIndex) {
			randomIndex = Math.floor(Math.random() * currentIndex);
			currentIndex -= 1;

			temporaryValue = array[currentIndex];
			array[currentIndex] = array[randomIndex];
			array[randomIndex] = temporaryValue;
		}
		return array;
	}
	
	static ready(length, divs, duration){
		length = Math.floor(length/divs)*divs;
		let blocklen = length/divs;
		
		this.length   = length;
		this.divs     = divs
		this.blocklen = blocklen;
		this.duration = duration;
        
		for(let i=0; i<divs*divs; ++i){
			let can = document.createElement('canvas');
			can.height = blocklen;
            can.width  = blocklen;
						  
			this.canvas.push(can);
		}
	}
	
	static readyimage(img){
		let divs     = this.divs;
		let blocklen = this.blocklen;
		
		let imlength   = Math.min(img.height, img.width);
		imlength       = Math.floor(imlength/divs)*divs;
		let imblocklen = imlength/divs;
		
		for(let i=0; i<divs; ++i){
			for(let j=0; j<divs; ++j){
				let can = this.canvas[divs*i+j]
				can.getContext("2d").drawImage(img, j*imblocklen, i*imblocklen, imblocklen, imblocklen, 0, 0, blocklen, blocklen);
			}
		}
	}
	
	constructor(name){
		this.name        = name;
		this.imidarray   = [];
		this.idarray     = [];
		this.animcounter = 0;
		
		let length    = SortBox.length;
		let divs      = SortBox.divs;
		let blocklen  = SortBox.blocklen;
		let container = $("#sort"+name)
		container.css({"height": length + "px",
					   "width" : length + "px"});

        for(let i=0; i<divs; ++i){
            for(let j=0; j<divs; ++j){
                let can = $(document.createElement('canvas'));
                
                can.attr({"id": "canvas_"+name+"_"+(divs*i+j),
                          "height": blocklen,
                          "width": blocklen});
                
                can.css({"top": (i*blocklen) + "px", 
                         "left": (j*blocklen) + "px"});
                
                container.append(can);
            }
        }
        
    }
    
    updateimage(){
        let divs = SortBox.divs;
		let name = this.name;
		
        for(let i=0; i<divs*divs; ++i){
			let can = $("#canvas_"+name+"_"+i).get(0).getContext("2d");
			can.drawImage(SortBox.canvas[i], 0, 0);
        }
    }
    
    place(id, imid){
        let divs     = SortBox.divs;
        let blocklen = SortBox.blocklen;
        let name     = this.name;
        
        let i = Math.floor(imid / divs);
        let j = imid % divs;
        
        let ob = $("#canvas_"+name+"_"+id);
        
		ob.css({"top" : (i*blocklen) + "px",
                "left": (j*blocklen) + "px"});
    }
    
    swapimid(imid1, imid2){
        let idarray   = this.idarray;
        let imidarray = this.imidarray;
        
        let id1 = idarray[imid1];
        let id2 = idarray[imid2];
        
        this.place(id1, imid2);
        this.place(id2, imid1);
        
        idarray[imid1] = id2;
        idarray[imid2] = id1;
        
        imidarray[id1] = imid2;
        imidarray[id2] = imid1;
    }
    
    reset(){
        let divs = SortBox.divs;
        
        for(let i=0; i<divs*divs; ++i){
            this.idarray[i] = i;
            this.imidarray[i] = i;
            this.place(i, i);
        }
    }
    
    shuffle(){
        let divs = SortBox.divs;
        
        this.imidarray = [];
        this.idarray   = [];
        
        for(let i=0; i<divs*divs; ++i){
            this.imidarray.push(i);
        }
        
        SortBox.shufflearr(this.imidarray);
        
        for(let i=0; i<divs*divs; ++i){
            this.idarray[this.imidarray[i]] = i;
            this.place(i, this.imidarray[i]);
        }
    }
    
    apply_algo(sort){
        let swaparr  = sort(Array.from(this.idarray))
        let duration = SortBox.duration;
        let timeoutdur;
        
        for(let curswap=0; curswap<swaparr.length; ++curswap){
            timeoutdur = (1000*duration*curswap)/swaparr.length;
            
            this.animcounter = 0;
            let obj = this;
            
            setTimeout(function(){
                if(swaparr[obj.animcounter] != 0 && swaparr[obj.animcounter][0] != swaparr[obj.animcounter][1])
                    obj.swapimid(swaparr[obj.animcounter][0], swaparr[obj.animcounter][1]);
                obj.animcounter++;
                
            }, timeoutdur);
        }
        
        setTimeout(function(){
            AppHandler.anim_finished();
        }, timeoutdur+500);
    }
}

class algorithms {
    static bubble(arr){
        let swaparr = [];
        for(let i=0; i<arr.length; ++i){
            for(let j=1; j<arr.length-i; ++j){
                swaparr.push(0);
                if(arr[j-1] > arr[j]){
                    let tmp = arr[j];
                    arr[j] = arr[j-1];
                    arr[j-1] = tmp;
                    swaparr.push([j-1, j]);
                }
            }
        }
        return swaparr;
    }
    static selection(arr){
        let swaparr = [];
        for(let i=0; i<arr.length-1; ++i){
            let smallest = i;
            for(let j=i+1; j<arr.length; ++j){
                swaparr.push(0);
                if(arr[j] < arr[smallest]){
                    smallest = j;
                }
            }
            if(smallest != i){
                let tmp = arr[smallest];
                arr[smallest] = arr[i];
                arr[i] = tmp;
                swaparr.push([smallest, i]);
            }
        }
        return swaparr;
    }
    static insertion(arr){
        let swaparr = [];
        for(let i=1; i<arr.length; ++i){
            let j=i-1
            while(j>=0 && arr[j] > arr[j+1]){
                swaparr.push(0);
                let tmp = arr[j+1];
                arr[j+1] = arr[j];
                arr[j] = tmp;
                swaparr.push([j, j+1]);
                j--;
            }
        }
        return swaparr;
    }
    static merge(arr){
        let swaparr = [];
        let x = function(mergearr, start, end){
            if(start >= end) return;
            
            let pivot = Math.floor((start+end)/2);
            
            x(mergearr, start, pivot);
            x(mergearr, pivot+1, end);
            
            for(let i=start+1; i<end+1; ++i){
                let j=i-1;
                while(j>=start && mergearr[j] > mergearr[j+1]){
                    swaparr.push(0);
                    let tmp = mergearr[j+1];
                    mergearr[j+1] = mergearr[j];
                    mergearr[j] = tmp;
                    swaparr.push([j, j+1]);
                    j--;
                }
            }
        }
        x(arr, 0, arr.length-1);
        return swaparr;
    }
    static shell(arr){
        let swaparr = [];
        
        let part = 1;
        while(part < arr.length) part = 3*part + 1;
        part = (part-1)/3;
        
        while(part > 0){
            for(let i=part; i<arr.length; i+=part){
                let j = i-part;
                while(j >= 0 && arr[j] > arr[j+part]){
                    swaparr.push(0);
                    let tmp = arr[j+part];
                    arr[j+part] = arr[j];
                    arr[j] = tmp;
                    swaparr.push([j, j+part]);
                    j -= part;
                }
            }
            part = (part-1)/3;
        }
        
        return swaparr;
    }
    static quick(arr){
        
        let swaparr = [];
        
        let x = function(quickarr, low, high){
            if(low >= high) return;
            
            let pivot = quickarr[high];
            let i = low;
            
            for(let j=low; j<high; ++j){
                swaparr.push(0);
                if(quickarr[j] < pivot){
                    let tmp = quickarr[j];
                    quickarr[j] = quickarr[i];
                    quickarr[i] = tmp;
                    swaparr.push([i, j]);
                    i++;
                }
            }
            
            let tmp = quickarr[high];
            quickarr[high] = quickarr[i];
            quickarr[i] = tmp;
            swaparr.push([i, high]);
            
            x(quickarr, low, i-1);
            x(quickarr, i+1, high);
        }
        
        x(arr, 0, arr.length-1);
        
        return swaparr;
    }
}

class AppHandler {
    static numviews = 6;
    static duration = 6;
    static length = 270;
    static divs = 10;
    static views = [];
    
    static ready(){
        
        SortBox.ready(this.length, this.divs, this.duration);
        
        for(let i=0; i<this.numviews; ++i){
            this.views.push(new SortBox(i.toString()));
        }
    
    }
    
    static create(){
        let img = ImageHandler.image();
        
        SortBox.readyimage(img);
        
        for(let i=0; i<this.numviews; ++i){
            this.views[i].updateimage();
        }
    
    }
    
    static reset(){
        for(let i=0; i<this.numviews; ++i){
            this.views[i].reset();
        }
    }
    
    static shuffle(){
        for(let i=0; i<this.numviews; ++i){
            this.views[i].shuffle();
        }
    }
    
    static sort(){
        this.views[0].apply_algo(algorithms.bubble);
        this.views[1].apply_algo(algorithms.selection);
        this.views[2].apply_algo(algorithms.insertion);
        this.views[3].apply_algo(algorithms.merge);
        this.views[4].apply_algo(algorithms.shell);
        this.views[5].apply_algo(algorithms.quick);
    }
    
    static anim_finished(){
        frontend_app.enable("app_buttons_shuffle");
    }
}

class Frontend {
    
    static show(){
        $("#"+this.id).show()
    }
    
    static hide(){
        $("#"+this.id).hide()
    }
    
    static enable(id){
        $("#"+id).removeAttr("disabled");
    }
    
    static disable(id){
        $("#"+id).attr("disabled", "disabled");
    }
}

class frontend_upload extends Frontend {
    
    static id = "frontend_upload";
    
    static ready(){
        $("#upload_urlbutton").click(function(){
            frontend_loading.show();
            frontend_upload.hide();
            
            let url = $("#upload_url").val();
            
            ImageHandler.img_src(url);
            
            FormHandler.set_type("url", url);
        });
        
        $("#upload_file").change(function(){
            frontend_loading.show();
            frontend_upload.hide();
            
            if(this.files && this.files[0]){
                ImageHandler.img_src(URL.createObjectURL(this.files[0]));
                FormHandler.set_type("file", this.files[0]);
            }
            
        });

        $("#upload_sample").click(function(){
            frontend_loading.show();
            frontend_upload.hide();
            
            let images = ["https://www.lightstalking.com/wp-content/uploads/cityscape_1557459555-1024x684.jpeg",
                          "https://miro.medium.com/max/3000/1*MI686k5sDQrISBM6L8pf5A.jpeg",
                          "https://media.sciencephoto.com/image/c0384612/800wm",
                          "https://img.freepik.com/free-vector/space-tour-illustration_153233-85.jpg?size=338&ext=jpg"];
            
            let url = images[Math.floor(Math.random()*images.length)];
            
            ImageHandler.img_src(url);
            
            FormHandler.set_type("url", url);
        });
    }
}

class frontend_loading extends Frontend {
        
    static id = "frontend_loading";
    
}

class frontend_app extends Frontend {
    
    static id = "frontend_app";
    
    static ready(){
        
        $("#app_buttons_new").click(function(){
            window.location.reload();
        });
        
        $("#app_buttons_reset").click(function(){
            AppHandler.reset();
            frontend_app.disable("app_buttons_reset");
            frontend_app.enable("app_buttons_shuffle");
            frontend_app.disable("app_buttons_sort");
        });
        
        $("#app_buttons_shuffle").click(function(){
            AppHandler.shuffle();
            frontend_app.enable("app_buttons_reset");
            frontend_app.enable("app_buttons_sort");
        });
        
        $("#app_buttons_sort").click(function(){
            AppHandler.sort(); 
            frontend_app.disable("app_buttons_reset");
            frontend_app.disable("app_buttons_shuffle");
            frontend_app.disable("app_buttons_sort");
        });
        
        $("#app_buttons_export").click(function(){
            frontend_export.show();
            frontend_app.hide();
            
            $.ajax({
                type: "POST",
                url: "export.php", 
                processData: false,
                contentType: false,
                cache: false,
                data: FormHandler.data(), 
                success: function(data){
                    frontend_export.token = data.trim();
                    frontend_export.next_state();
                },
                error: function(){
                    alert("hmm");
                }
            });
            
            frontend_export.ajax_interval = setInterval(function(){
                $.ajax({
                    type: "POST",
                    url: "status.php",
                    cache: false,
                    data: {"token": frontend_export.token}, 
                    success: function(data){
                        if(parseInt(data.trim()) > frontend_export.state)
                            frontend_export.next_state();
                    },
                    error: function(){
                        alert("hmm");
                    }
                });                
            }, 1000);
            
        });
    }   
}

class frontend_export extends Frontend {
    
    static id = "frontend_export";
    static token = "";
    static state = -1;
    static ajax_interval = null;
    
    static ready(){
        $("#export_download_button").click(function(){
            window.location = "download.php?token="+frontend_export.token;
        });
    }
    
    static next_state(){
        this.state++;
        if(this.state == 0){
            $("#export_upload_done").css("visibility","visible");
            $("#export_frames").css("visibility","visible");
        } else if(this.state == 1){
            $("#export_frames_done").css("visibility","visible");
            $("#export_render").css("visibility","visible");
        } else if(this.state == 2){
            $("#export_render_done").css("visibility","visible");
            $("#export_compress").css("visibility","visible");
        } else if(this.state == 3){
            $("#export_compress_done").css("visibility","visible");
            $("#export_download").css("visibility","visible");
            clearInterval(this.ajax_interval);
        }
    }
    
}

class ImageHandler {
    static img = new Image();
    
    static image(){
        return this.img;
    }
    
    static img_onload(func){
        this.img.onload = func;
    }
    
    static img_src(src){
        this.img.src = src;
    }
}

class FormHandler {
    // "type" : [url, file]
    
    static formdata = new FormData();
    
    static set_type(type, data){
        this.formdata.append("type", type);
        if(type == "url")
            this.formdata.append("url", data);
        else if(type == "file")
            this.formdata.append("file", data, "image");
    }
    
    static data(){
        return this.formdata;
    }
}

$(document).ready(function(){
    
    frontend_upload.ready();
    frontend_app.ready();
    frontend_export.ready();
    
    AppHandler.ready();
    
    ImageHandler.img_onload(function(){
        AppHandler.create();
        
        frontend_app.show();
        frontend_loading.hide();
        frontend_app.enable("app_buttons_shuffle");
    });

});

