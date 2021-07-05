document.addEventListener("DOMContentLoaded",function(e){
    //Reset File functions
    document.forms["agent_picker"].reset();
   /*
    //Reset File functions - END
    //Common functions
    function removeChildren(node){
        while (node.firstChild){
            node.removeChild(node.firstChild);
        }
    }

    function currencyConverter(value){
        const options = {style: "currency", currency:"EUR"};
        const formatter = new Intl.NumberFormat("en-US", options);
        return formatter.format(value);
    }

    function convertCurrency(value){
        return Number(value.replace(/[^0-9.-]+/g,""));
    }

    */

    function toggleClass(element, clas, time){
        function addClass(element, clas){
            element.classList.add(clas);
        }
        function removeClass(element, clas){
            element.classList.remove(clas);
        }
        addClass(element, clas);
        setTimeout(function(){removeClass(element, clas)}, time);
    }

    /*

    function fillHand(element, array){
        array.forEach(function(item){
            var card = document.createElement("li");
            card.innerHTML = item;
            element.appendChild(card);
        });
    }

    function toggleBetContainer(){
        var container = document.getElementById("bet_container");
        if (container.style.display == "none" || container.style.display == ""){
            container.style.display = "block";
            toggleClass(container, "high_border", 2000);
        }else{
            document.getElementById("bet_value").value = "";
            container.style.display = "none";
        }
    }

    function toggleError(expression, parent, message, cls){
        var last_error = parent.querySelector(".err." + cls);
        if (expression){
            if (last_error == null){
                var text_error = "<p class='err " + cls + "'>" + message + "</p>";
                var error_element = document.createElement("p");
                error_element.innerHTML = text_error;
                parent.append(error_element);              
                
            }

            return true;

        }else {            
            if (last_error != null){
                last_error.parentNode.removeChild(last_error);
                last_error = null;
            }
        }
        return false;
    }

    function checkStatus(obj){
        var player = document.getElementById("player_hand");
        var name = document.getElementById("sent_name").value;
        var dealer = document.getElementById("dealer_hand");

        removeChildren(player);
        fillHand(player, obj[name]);
        removeChildren(dealer);
        fillHand(dealer, obj["Dealer"]);

        if (obj["Status"] != "on"){       
            document.querySelectorAll(".instruction").forEach(function(element){
                element.disabled = true;
            });

            toggleError(1==1, player.parentNode, obj["Status"], "outcome");
            
            setTimeout(function(){
                removeChildren(player);
                removeChildren(dealer);
                toggleError(1==2, player.parentNode, obj["Status"], "outcome");
                document.getElementById("total_cash").value = currencyConverter(obj["Player_cash"]);
                document.getElementById("current_bet").value = currencyConverter(0);
                if (obj["Continuity"] != null){
                    gameOver(obj["Continuity"]);
                }else {
                    toggleBetContainer();
                }                
            }, 5000);           

        }        
    }

    function gameOver(message){
        alert(message);

        document.getElementById("total_cash").value = currencyConverter(0);
        document.getElementById("current_bet").value = currencyConverter(0);
        document.getElementById("player_info").style.visibility = "hidden";
        document.getElementById("name").innerHTML = "Player:";
        document.getElementById("play").disabled = false;
        document.getElementById("sent_name").value = "";
        document.getElementById("cash").value = "";
        document.getElementById("player_info").childNodes.forEach(function(element){
            element.disabled = false;
        });

    }

    //Common functions - END
    */
    //AJAX Functions
    function sendInfo(method, url, async, data, callback){
        var request = new XMLHttpRequest();
        request.onreadystatechange = function(){
            if (request.readyState == 4){
                if (request.status == 200){
                    callback(request.responseText);
                }
            }
        }

        request.open(method, url, async);
        request.send(data);
    }

    function BuildForm(obj){
        var data = new FormData();
        const ks = Object.keys(obj);
        ks.forEach((key, index)=>{data.append(key, obj[key]);});
        return data;
    }

    //Ajax Functions - END
    /*
    //Events
    /////Play!
    document.getElementById("play").addEventListener("click", function(e){
        document.getElementById("player_info").style.visibility = "visible";
    });
    /////Start!
    document.getElementById("player_info").addEventListener("submit", function(e){
        var name = document.getElementById("sent_name").value;
        var cash = document.getElementById("cash").value;

        if(toggleError(name=="", e.target, "Error! Player's name must be filled in!", "name")){
            e.preventDefault();
            return;
        }

        if (toggleError((cash == "" || cash < 1000 || isNaN(cash)), e.target,"Error! Cash must be greater than €1,000!", "cash")) {
            e.preventDefault();
            return;
        }

        sendInfo("POST", "/start", false, BuildForm({name: name, initial_cash: cash, 
                                                     allow_debt: document.getElementById("indebtness").value}),
                 (text)=>{});

        
        document.getElementById("name").innerHTML = name + ":";

        document.getElementById("play").disabled = true;
        
        this.childNodes.forEach(function(element){
            element.disabled = true;
        });

        var cash_element = document.getElementById("total_cash");
        cash_element.value = currencyConverter(cash);
        toggleClass(cash_element, "high_input_text", 2000);


        toggleBetContainer();

        e.preventDefault();
    });
    /////Place Bet
    document.getElementById("bet_placer").addEventListener("click", function(e){
        var bet = document.getElementById("bet_value").value;
        var remaining_cash = document.getElementById("total_cash").value;
        var money = convertCurrency(remaining_cash);
        var debt = document.getElementById("indebtness").value;
        var evaluation = (bet < 0 || bet == "" || (bet > money && debt =="N"));

        if (!toggleError(evaluation, e.target.parentNode, "Bet value must be between €1 and " + remaining_cash, "bet")){
            document.getElementById("total_cash").value = currencyConverter(money - bet);
            document.getElementById("current_bet").value = currencyConverter(bet);            
            document.querySelectorAll(".instruction").forEach(function(element){
                element.disabled = false;                          
            });

            toggleBetContainer();

            sendInfo("POST", "/bet", false, BuildForm({value: bet}),(text)=>{
                    var obj = JSON.parse(text);
                    checkStatus(obj);
            });           

        }
    });

    /////Hit & Stand
    document.querySelectorAll(".instruction").forEach(function(element){
        element.addEventListener("click", function(e){
            sendInfo("POST", "/action", false, BuildForm({action: e.target.value}), (text)=>{
                var obj = JSON.parse(text);
                checkStatus(obj);
            })
        });
    });

    */
    document.getElementById("stop").disabled = true;
    document.getElementById("play").disabled = true;

    function notice(){
        var picker =  document.getElementById("agents");
        if (picker.value == ""){
            toggleClass(picker, "red_light", 1000);
        }        
    }    
    setInterval(function(){notice()}, 2000);

    document.getElementById("agents").addEventListener("change", function(e){
        if (this.value != ""){
            var play = document.getElementById("play");
            play.disabled = false;
            play.classList.remove("disabled");
            play.classList.add("enabled");
        }
    });

    document.getElementById("agent_picker").addEventListener("submit", function(e){
        var picker =  document.getElementById("agents");
        if (picker.value != ""){
            var play = document.getElementById("play");
            play.disabled = true;
            play.classList.remove("enabled");
            play.classList.add("disabled");

            var stop = document.getElementById("stop");
            stop.disabled = false;
            stop.classList.remove("disabled");
            stop.classList.add("enabled");

            picker.setAttribute("disabled", "disabled");

            document.querySelector(".invisible").classList.remove("invisible");
            
            sendInfo("POST", "/start", true, BuildForm({agent: picker.value}), (text)=>{
                var list = JSON.parse(text)
                for (element of list){
                    console.log(element)
                }
                var llista = new Array(1,2,3)
                el = llista.shift()
                console.log(el);
                console.log(llista.length);

            });       
        }

        e.preventDefault();
    });

    document.getElementById("stop").addEventListener("click", function(e){
            location.reload();
    });

    document.querySelector("#rules ul").addEventListener("mouseover", function(e){
        var rules = document.querySelector(".modal");
        if (!rules.classList.contains("animated-modal")){
            rules.classList.remove("unanimated-modal");
            rules.classList.add("animated-modal");            
        }


    });

    
    document.querySelector(".modal").addEventListener("mouseout", function(e){
        var rules = document.querySelector(".modal");
        rules.classList.add("unanimated-modal");
        setTimeout(function(){rules.classList.remove("animated-modal");}, 500);

    } );
   
    //Events - END
});