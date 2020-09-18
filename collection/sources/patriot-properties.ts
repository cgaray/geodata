import axios, { AxiosInstance } from 'axios';
import axiosCookieJarSupport from 'axios-cookiejar-support';
import * as tough from 'tough-cookie';
import jsdom from 'jsdom';
const { JSDOM } = jsdom;

// @ts-ignore
axiosCookieJarSupport.default(axios);

interface PatriotPropertiesQuery {
  accountNumber: number;
}

interface SearchQuery {
  SearchParcel?: string;
  SearchBuildingType?: string;
  SearchLotSize?: number;
  SearchLotSizeThru?: number;
  SearchTotalValue?: number;
  SearchTotalValueThru?: number;
  SearchOwner?: string;
  SearchYearBuilt?: number;
  SearchYearBuiltThru?: number;
  SearchFinSize?: number;
  SearchFinSizeThru?: number;
  SearchSalePrice?: number;
  SearchSalePriceThru?: number;
  SearchStreetName?: string;
  SearchBedrooms?: number;
  SearchBedroomsThru?: number;
  SearchNeighborhood?: string;
  SearchNBHDescription?: string;
  SearchSaleDate?: string;
  SearchSaleDateThru?: string;
  SearchStreetNumber?: number;
  SearchBathrooms?: number;
  SearchBathroomsThru?: number;
  SearchLUC?: string;
  SearchLUCDescription?: string;
  SearchBook?: number;
  SearchPage?: number;
}

export default class PatriotPropertiesAPI {
  apiConn: AxiosInstance;
  connInitialized: boolean;

  constructor(city: string) {
    this.apiConn = axios.create({
      baseURL: `http://${city}.patriotproperties.com`,
      // @ts-ignore
      jar: new tough.default.CookieJar(),
      withCredentials: true,
    });
    this.connInitialized = false;
  }

  initCookie = () => this.apiConn.get('/');

  buildQuery = (data: Record<string, string | number>) => Object.keys(data).map(k => `${k}=${data[k]}`).join('&');

  processSearchResultTableRow = (row: HTMLTableRowElement) => {
    const cols = row.querySelectorAll('td');
    const parcelId = cols[0].textContent;
    const streetNum = /^\d*/.exec(cols[1].textContent)[0];
    const streetName = cols[1].querySelector('a').textContent;
    const owners = [];
    cols[2].querySelectorAll('a').forEach(a => owners.push(a.textContent));
    const yearBuilt = cols[3].querySelectorAll('a')[0]?.textContent;
    const buildingType = cols[3].querySelectorAll('a')[1]?.textContent;
    const value = cols[4].textContent;
    const beds = /^\d*/.exec(cols[5]?.textContent)[0];
    const baths = /\d*$/.exec(cols[5]?.textContent)[0];
    const lotSize = /^(\d|,)*/.exec(cols[6]?.textContent)[0];
    const finArea = /(\d|,)*$/.exec(cols[6]?.textContent)[0];
    const luc = cols[7].querySelectorAll('a')[0]?.textContent;
    const description =  cols[7].querySelectorAll('a')[1]?.textContent;
    const neighborhood = cols[8].textContent;
    const saleDate =  /^\d{1,2}\/\d{1,2}\/\d{4}/.exec(cols[9]?.textContent)?.pop();
    const salePrice = /(\d|,)*$/.exec(cols[9]?.textContent)?.pop();
    return {
      baths: baths ? parseInt(baths) : undefined,
      beds: beds ? parseInt(beds) : undefined,
      buildingType,
      description,
      finArea,
      lotSize,
      luc,
      neighborhood,
      owners,
      parcelId,
      saleDate,
      salePrice,
      streetName,
      streetNum: parseInt(streetNum),
      value,
      yearBuilt: yearBuilt ? parseInt(yearBuilt) : undefined,
    };
  }

  getBookPageCount = async (book: number) => {
    const reqData = {
      SearchBook: `${book}`,
      SearchSubmitted: "yes",
      cmdGo: "Go",
    };
    const response = await this.apiConn.post('/SearchResults.asp', this.buildQuery(reqData));
    const dom = new JSDOM(response.data);
    const { body } = dom.window.document;
    const pageCountText = body.querySelector('tr').textContent;
    const countStr = /page \d* of (\d*)/.exec(pageCountText)?.pop();
    return countStr ? parseInt(countStr) : undefined;
  }

  getPropertyList = async (query: SearchQuery) => {
    const reqData = {
      ...query,
      SearchSubmitted: "yes",
      cmdGo: "Go",
    };
    const response = await this.apiConn.post('/SearchResults.asp', this.buildQuery(reqData));
    const dom = new JSDOM(response.data);
    const { body } = dom.window.document;

    // Pull the results out of the table
    const tableRows = body.querySelector('#T1').querySelector('tbody').querySelectorAll('tr');
    const res = [];
    tableRows.forEach(r => res.push(this.processSearchResultTableRow(r)));
    return res;
  };

  getProperty = async ({accountNumber}: PatriotPropertiesQuery) => {
    if (!this.connInitialized) await this.initCookie();
    const prelimResponse = await this.apiConn.get(`/Summary.asp?AccountNumber=${accountNumber}`);
    if (prelimResponse.status !== 200)
      throw Error(prelimResponse.data);
    const response = await this.apiConn.get(`/summary-bottom.asp`);
    const dom = new JSDOM(response.data);
    const body = dom.window.document.body;
    console.log(body.outerHTML);
  };
}
