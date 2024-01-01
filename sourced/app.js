const express = require('express');
const helmet = require('helmet');
const morgan = require('morgan');
const pupp = require("puppeteer");
const {isIPV4Address} = require("ip-address-validator");
const cors = require('cors');
const isReachable = require('is-reachable');
require("dotenv").config();

const app = express();

app.use(helmet());
app.use(morgan('tiny'));
app.use(cors());

let system = {
    browser : null,
    printer : null,
    timeout : 5000,
    error : []
};

let response_message = {
    info: {
        api_name: "Printer Info Snatcher",
        supported_printers: "HP Enterprise M-series",
        request_format: "http://app-ip-address?ip=w.x.y.z",
    }
};

(async () => {
    system.browser = await pupp.launch({
        headless: true,
        devtools: false,
        ignoreHTTPSErrors: true,
        args: ['--incognito', '--disable-gpu', '--disable-dev-shm-usage', '--disable-setuid-sandbox', '--no-sandbox']
    });
})();

let browser_params = {
    waitUntil: 'networkidle0',
    timeout: system.timeout
};

let request_message = {};
let printer_message = {};

class Printer {
    constructor(host) {
        this.host = host;
        request_message.ip = host;

        this.name = null;
        this.type = null;
        this.model = null;
        this.serial = null;
        this.location = null;
        this.trays = {};
        this.supplies = {};
        this.errors = null;
    }
    async get_info() {
        // See if printer is online, if not return an error
        if (!await isReachable(this.host)) {
            printer_message = {
                status: "error",
                message: "Printer unreachable"
            };
        }

        else {
            const result = [await get_device_details(this), await get_supply_details(this), await get_tray_details(this)];

            if (result.includes(-1)) {
                printer_message = {
                    status: "error",
                    message: system.error
                };
            }

            else {
                this.type = await this.model.includes("Color") ? "color" : "grayscale";

                printer_message = {
                    status: "success",
                    message: this
                };
            }
        }
    }
}

async function get_device_details(printer_obj){
    const page = await system.browser.newPage();

    try {
        await page.goto(`https://${printer_obj.host}/hp/device/DeviceInformation/View`, browser_params);

        printer_obj.model = await page.evaluate(()=> {
            return document.querySelector("#ProductName").textContent;
        })
        printer_obj.name = await page.evaluate(()=> {
            return document.querySelector("#DeviceName").textContent;
        });
        printer_obj.serial = await page.evaluate(()=> {
            return document.querySelector("#DeviceSerialNumber").textContent;
        });
        printer_obj.location = await page.evaluate(()=> {
            return document.querySelector("#DeviceLocation").textContent;
        });
    }
    catch {
        system.error.push("Cannot get device details");
        return -1;
    }
    finally {
        await page.close(); // this will be executed regardless of the return statement above
    }
}

async function get_supply_details(printer_obj){
    const page = await system.browser.newPage();

    try {
        await page.goto(`https://${printer_obj.host}/hp/device/DeviceStatus/Index`, browser_params);

        let cartridges = await page.evaluate(() => {
            return Array.from(document.querySelectorAll(".cartridges .consumable h2"))
                .map (x=> x.textContent);
        });

        let levels = await page.evaluate(() => {
            return Array.from(document.querySelectorAll(".cartridges .consumable .plr"))
                .map (x=> x.textContent.replace("%*", ''));
        });

        for(let i = 0; i < cartridges.length; ++i) {
            printer_obj.supplies[cartridges[i]] = levels[i];
        }

    }
    catch {
        system.error.push("Cannot get cartridge info");
        return -1;
    }
    finally {
        await page.close();
    }
}

async function get_tray_details(printer_obj) {
    const page = await system.browser.newPage();

    try {
        await page.goto(`https://${printer_obj.host}/hp/device/DeviceStatus/Index`, browser_params);

        async function get_tray_info(tray_no) {
            return {
                status: (await page.evaluate((tray_no) => {
                    return document.querySelector(`#TrayBinStatus_${tray_no}`).textContent;
                }, tray_no)).replace('%', ''),
                capacity: await page.evaluate((tray_no) => {
                    return document.querySelector(`#TrayBinCapacity_${tray_no}`).textContent;
                }, tray_no),
                size: (await page.evaluate((tray_no) => {
                    return document.querySelector(`#TrayBinSize_${tray_no}`).textContent;
                }, tray_no)).replace("▭", '').trim(),
                type: await page.evaluate((tray_no) => {
                    return document.querySelector(`#TrayBinType_${tray_no}`).textContent;
                }, tray_no)
            };
        }

        async function tray_exists(tray_no) {
            let div = await page.evaluate((tray_no) => {
                return document.querySelector(`#TrayBin_Tray${tray_no}`);
            }, tray_no);
            return div != null;
        }

        if ((await page.$("#TrayBin_MultipurposeTray"))) {
            printer_obj.trays["Tray 1"] = await get_tray_info(1);
        }

        let tray = 2;
        while (await tray_exists(tray)) {
            printer_obj.trays[`Tray ${tray}`] = await get_tray_info(tray);
            ++tray;
        }

        let machine_status_array = await page.evaluate(() => {
            return Array.from(document.querySelectorAll("#MachineStatus"))
                .map(x => x.textContent.trim())
        });

        printer_obj.errors = machine_status_array.filter(msg => msg !== "Ready");
    }
    catch {
        system.error.push("Cannot get tray info");
        return -1;
    }
    finally {
        await page.close();
    }
}

app.get('/', async (req, res) =>
{
    let ip = req.query.ip;
    if (ip === undefined)
        res.status(200).json(response_message);

    else {
        ip = ip.trim();
        if (isIPV4Address(ip))
        {
            system.printer = new Printer(ip);
            await system.printer.get_info();
            response_message.response = printer_message;
            response_message.request = request_message;

            res.status(200).json(response_message);

            system.printer = null;
            system.error = [];
        }

        else {
            response_message.response = {
                status: "error",
                message: "Invalid IPV4 Address"
            }
            res.status(500).json(response_message);
        }
    }

});

let port = 8000;
app.listen(port);
