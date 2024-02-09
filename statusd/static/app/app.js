(function () {

    window.addEventListener("load", init);

    const ACCARDION_ERROR_ICON = "static/icons/error.svg";
    const ACCARDION_CAUTION_ICON = "static/icons/caution.svg";
    const ACCARDION_NO_ERROR_ICON = "static/icons/no-errors.svg";

    const DEFAULT_PROGRESS_BAR_VALUE = 0;

    // Functions that will be called when page is opened. If error occurs, it will display it.

    let location = window.location.href.split("/")[3];
    function init() {
        $.ajax({
            url: "api/printers",
            type: "GET",
            data: {
                "location": location
            },
            success: (data) => {
                data.forEach( (printer) => {
                    populateCard(printer);
                });
            }
        });
    }

    /**
     * Takes in a parsed JSON data and populates the cards according to the data.
     * @param {JSON} printer_data - card that needs to be inserted in the main view.
     */
    function populateCard(printer_data) {
        let card = createCard(printer_data);
        setPrinterStatus(card, printer_data);
        setName(card, printer_data);
        setSupplies(card, printer_data);
        setTrays(card, printer_data);
        let container = document.getElementById("print-status");
        container.children[0].appendChild(card);
    }

    /**
     * Takes in a JSON data and  a card HTML element and sets up printer status according to the data.
     * @param {HTMLElement} card - card that needs to be set up.
     * @param {JSON} data - data according to which the card is set up.
     */
    function setPrinterStatus(card, data) {
        let isError = (data.response.status === "error");
        $(card).attr("class", "card");
        if (isError) {
            $(card).addClass("attention");
        } else {
            let haveErrors = data.response.message.errors.length > 0;
            if (haveErrors) {
                $(card).addClass("warning");
                $(card).find(".accordion-button img").attr("src", ACCARDION_CAUTION_ICON);
                setErrors(card, data);
            } else {
                $(card).addClass("ready")
                $(card).find(".accordion-button img").attr("src", ACCARDION_NO_ERROR_ICON);
                noErrors(card);
            }
        }
    }

    /**
     * Takes in a JSON data and a card HTML element and sets up errors for that card.
     * @param {HTMLElement} card - card that needs to be set up.
     * @param {JSON} data - data from which the error messages is extracted.
     */
    function setErrors(card, data) {
        data = data.response.message.errors;
        $(card).find(".accordion-body").innerHTML = "";
        for (let i = 0; i < data.length; i++) {
            let result = document.createElement("p");
            result.appendChild(document.createTextNode("- " + data[i]));
            $(card).find(".accordion-body").append(result);
        }
    }

    /**
     * Takes in card HTML element and sets up no Errors for that card.
     * @param {HTMLElement} card - card that needs to be set up.
     */
    function noErrors(card) {
        $(card).find(".accordion-body").innerHTML = "";
        let result = document.createElement("p");
        result.classList.add("text-center");
        result.appendChild(document.createTextNode("No Errors!"));
        $(card).find(".accordion-body").append(result);
    }

    /**
     * Takes in a JSON data and a card HTML element and sets name of the printer for that card.
     * @param {HTMLElement} card - card that needs to be set up.
     * @param {JSON} data - data from which the name of the card is extracted.
     */
    function setName(card, data) {
        $(card).find('.card-header-text').text(data.meta.name);
    }

    /**
     * Takes in a JSON data and a card HTML element and sets up multiple trays
     * of the printer for that card.
     * @param {HTMLElement} card - card that needs to be set up.
     * @param {JSON} data - data from which the trays' informaton is extracted.
     */
    function setTrays(card, data) {
        data = data.response.message.trays
        let counter = 1;
        for (let key in data) {
            let val = data[key].status.toLowerCase();
            key = key.toLocaleLowerCase().split(" ");
            setTray(card, "paper-tray-" + counter, val);
            counter++;
        }
    }

    /**
     * Takes in card HTML element and sets up single tray of the printer for that card.
     * @param {HTMLElement} card - card that needs to be set up.
     * @param {string} id - specific number of the tray for that specific card
     * @param {string} value - value to which the trays are set
     */
    function setTray(card, id, value) {
        card = $(card);
        if (value === "ok" || value === "40 - 100") {
            value = 100;
        } else if (value === "empty" || value.length === 0) {
            value = 0;
        } else {
            let sorted = value.replace(/\D/g, ' ').split(/\s+/);
            if (sorted.length === 1) {
                value = parseInt(sorted);
            } else {
                let sum = 0;
                let count = 0;
                for (let i = 0; i < sorted.length; i++) {
                    if (!isNaN(sorted[i]) && sorted[i] !== "") {
                        sum += parseInt(sorted[i]);
                        count += 1;
                    }
                }
                value = sum / count;
            }
        }
        let classes = card.find("#container-" + id);
        classes.attr("class", "paper-tray");
        if (value >= 60) {
            classes.addClass("ready");
            classes.children(".error-msg").text("")
        } else if (value > 0 && value < 60) {
            classes.addClass("warning");
            classes.children(".error-msg").text("")
        } else if (value === 0) {
            classes.addClass("attention");
            classes.addClass("is-error");
            classes.children(".error-msg").text("Empty")
        }
        setProgressBar(card.find("#" + id), value);
    }

    /**
     * Takes in a JSON data and a card HTML element and sets up multiple supply progress bars for the card
     * @param {HTMLElement} card - card that needs to be set up.
     * @param {JSON} data - data from which progressbar info is extracted.
     */
    function setSupplies(card, data) {
        data = data.response.message.supplies;
        for (let key in data) {
            let val = data[key];
            key = key.toLocaleLowerCase().split(" ");
            setSupply(card, key[0], key[1], val);
        }
    }

    /**
     * Takes in the card which supply progressbor needs to be set up and sets up the
     * progressbar according to given parameters
     * @param {HTMLElement} card - card which supply progressbar needs to be set up.
     * @param {string} type - color of the supply progress bar
     * @param {string} kind - type of supply.
     * @param {string} value - value to which supply progressbar needs to be set up.
     */
    function setSupply(card, type, kind, value) {
        type = type.toLocaleLowerCase().split(" ")[0];
        card = $(card);
        let sorted = value.replace(/\D/g, ' ').split(/\s+/);
        if (sorted.length === 1) {
            value = parseInt(sorted);
        } else {
            let sum = 0;
            let count = 0;
            for (let i = 0; i < sorted.length; i++) {
                if (!isNaN(sorted[i]) && sorted[i] !== "") {
                    sum += parseInt(sorted[i]);
                    count += 1;
                }
            }
            value = sum / count;
        }
        setProgressBar(card.find("#" + type + "-" + kind), value);
    }

    /**
     * Takes in a data about the progress bar and sets up the value for it.
     * @param {HTMLElement} progressBar - Progress bar that needs to be set up
     * @param {float} val - value to which progressbar needs to be set up.
     */
    function setProgressBar(progressBar, val) {
        progressBar.attr({"aria-valuenow": val});
        progressBar.animate({"width": val + "%"}, 500);
    }

    /**
     * Takes in a data about a card and generates the card according to it.
     * @param {boolean} isColor - true if it is a color printer. False, otherwise.
     * @param {JSON} data - data by which the printer is set up.
     * @returns {HTMLElement} - ready but empty card.
     */

    // Main card
    function createCard(data) {
        let card = document.createElement("div");
        const isColor = data.meta.type === "color";

        card.classList.add("card", (isColor) ? "color" : "black-white-printer");

        // Header
        let cardHeader = document.createElement("div");
        cardHeader.classList.add("card-header", "text-center");
        let cardHeaderText = document.createElement("div");
        cardHeaderText.classList.add("card-header-text", "text-center");
        cardHeader.appendChild(cardHeaderText);

        // Body
        let body = document.createElement("div");
        body.classList.add("card-body");

        let progressContainer = document.createElement("div");
        let kitName = document.createElement("div");

        if (isColor) {
            // Cartridges
            progressContainer.classList.add("progress-container");
            kitName.appendChild(document.createTextNode("Cartridges"));
            progressContainer.appendChild(kitName);
            progressContainer.appendChild(createProgressBar('bg-yellow', false, "yellow-cartridge"));
            progressContainer.appendChild(createProgressBar('bg-magenta', false, "magenta-cartridge"));
            progressContainer.appendChild(createProgressBar('bg-cyan', false, "cyan-cartridge"));
            progressContainer.appendChild(createProgressBar('bg-black', false, "black-cartridge"));
            body.appendChild(progressContainer);

            // Kits
            progressContainer = document.createElement("div");
            progressContainer.classList.add("progress-container");
            kitName = document.createElement("div");
            kitName.appendChild(document.createTextNode("Fuser Kit"));
            progressContainer.appendChild(kitName);
            progressContainer.appendChild(createProgressBar('bg-success', false, "fuser-kit"));
            body.appendChild(progressContainer);

            // second kit
            progressContainer = document.createElement("div");
            progressContainer.classList.add("progress-container");
            kitName = document.createElement("div");
            kitName.appendChild(document.createTextNode("Transfer Kit"));
            progressContainer.appendChild(kitName);
            progressContainer.appendChild(createProgressBar('bg-success', false, "transfer-kit"));
            body.appendChild(progressContainer);

            // Paper trays
            progressContainer = document.createElement("div");
            progressContainer.classList.add("progress-container");
            kitName = document.createElement("div");
            kitName.appendChild(document.createTextNode("Paper Trays"));
            progressContainer.appendChild(kitName);
            for (let i = 0; i < 2; i++) {
                let currentBar = createProgressBar('test', true, ("paper-tray-" + (i + 1)));
                currentBar.querySelector(".tray-num").appendChild(document.createTextNode(i + 1));
                progressContainer.appendChild(currentBar);
            }
            body.appendChild(progressContainer);
        } else {
            // Cartridges
            progressContainer = document.createElement("div");
            progressContainer.classList.add("progress-container");
            kitName = document.createElement("div");
            kitName.appendChild(document.createTextNode("Cartridge"));
            progressContainer.appendChild(kitName);
            progressContainer.appendChild(createProgressBar('bg-black', false, "black-cartridge"));
            body.appendChild(progressContainer);
            // Kits
            progressContainer = document.createElement("div");
            progressContainer.classList.add("progress-container");
            kitName = document.createElement("div");
            kitName.appendChild(document.createTextNode("Maintenance Kit"));
            progressContainer.appendChild(kitName);
            progressContainer.appendChild(createProgressBar('bg-success', false, "maintenance-kit"));
            body.appendChild(progressContainer);
            // Trays
            progressContainer = document.createElement("div");
            progressContainer.classList.add("progress-container");
            kitName = document.createElement("div");
            kitName.appendChild(document.createTextNode("Paper trays"));
            progressContainer.appendChild(kitName);
            for (let i = 0; i < 5; i++) {
                let currentBar = createProgressBar('test', true, ("paper-tray-" + (i + 1)));
                currentBar.querySelector(".tray-num").appendChild(document.createTextNode(i + 1));
                progressContainer.appendChild(currentBar);
            }
            body.appendChild(progressContainer);
        }


        // Footer
        let cardMessageBlock = document.createElement("div");
        cardMessageBlock.classList.add("card-message-block");
        cardMessageBlock.appendChild(createMessageBlock(data));

        let cardMain = document.createElement("div");
        cardMain.classList.add("card-main-block");

        cardMain.appendChild(cardHeader);
        cardMain.appendChild(body);
        card.appendChild(cardMain);
        card.appendChild(cardMessageBlock);


        return card;
    }

    /**
     * Takes in a data about a card and generates the message dropdown menu.
     * @param {JSON} data - data by which the message dropdown menu is set up.
     * @returns {HTMLElement} - ready but empty message block.
     */
    function createMessageBlock(data) {

        let serial = data.response.message.serial;

        const accordionId1 = "accordion-parrent-id-" + serial;
        const accordionId2 = "accordion-child-id-" + serial;


        let accordion = document.createElement("div");
        accordion.classList.add("accordion");
        accordion.id = accordionId1;

        let accordionItem = document.createElement("div");
        accordionItem.classList.add("accordion-item");

        let accordionHeader = document.createElement("h2");
        accordionHeader.classList.add("accordion-header");
        accordionHeader.id = "headingOne";

        let accordionHeaderButton = document.createElement("button");
        accordionHeaderButton.classList.add("accordion-button", "collapsed");
        accordionHeaderButton.setAttribute("type", "button");
        accordionHeaderButton.setAttribute("data-mdb-toggle", "collapse");
        accordionHeaderButton.setAttribute("data-mdb-target", ("#" + accordionId2));
        accordionHeaderButton.setAttribute("aria-expanded", "true");
        accordionHeaderButton.setAttribute("aria-controls", accordionId1);

        let icon = document.createElement("img");
        icon.src = ACCARDION_CAUTION_ICON;
        icon.alt = "error-icon";
        accordionHeaderButton.appendChild(icon);


        let accordionCollapse = document.createElement("div");
        accordionCollapse.id = accordionId2;
        accordionCollapse.classList.add("accordion-collapse", "collapse");
        accordionCollapse.setAttribute("aria-labelledby", "headingOne");
        accordionCollapse.setAttribute("data-mdb-parent", ("#" + accordionId1));


        let accordionBody = document.createElement("div");
        accordionBody.classList.add("accordion-body");
        accordionBody.textContent = ""; // dummy text

        accordionCollapse.appendChild(accordionBody);
        accordionHeader.appendChild(accordionHeaderButton)
        accordionItem.appendChild(accordionHeader);
        accordionItem.appendChild(accordionCollapse);
        accordion.appendChild(accordionItem);

        return accordion;
    }

    /**
     * Takes in a color type about a progressbar and generates a single progressbar.
     * @param {string} color - Color of the progress bar
     * @param {boolean} isPaper - True if the progressbar is for paper trays. False, otherwise.
     * @param {string} id - name for the progressbar.
     * @returns {HTMLElement} - ready but empty progressbar.
     */
    function createProgressBar(color, isPaper, id) {
        let progress = document.createElement("div");
        progress.classList.add("progress");
        let progressBar = document.createElement("div");
        progressBar.classList.add("progress-bar", color);
        progressBar.setAttribute("id", id);

        progressBar.setAttribute("role", "progressbar");
        progressBar.setAttribute("aria-valuenow", DEFAULT_PROGRESS_BAR_VALUE);
        progressBar.setAttribute("aria-valuemin", "0");
        progressBar.setAttribute("aria-valuemax", "100");
        progressBar.style.width = DEFAULT_PROGRESS_BAR_VALUE + "%";
        progress.appendChild(progressBar);
        if (isPaper) {
            let paperTray = document.createElement("div");
            paperTray.classList.add("paper-tray");
            paperTray.setAttribute("id", "container-" + id);
            let trayNum = document.createElement("span");
            trayNum.classList.add("tray-num", color);
            let errorMsg = document.createElement("div");
            errorMsg.classList.add("error-msg");
            paperTray.appendChild(trayNum);
            paperTray.appendChild(errorMsg);
            paperTray.appendChild(progress);
            return paperTray;
        } else {
            return progress;
        }

    }


})();