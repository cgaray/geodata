import PatriotPropertiesAPI from './sources/patriot-properties';
import mongo from 'mongodb';

const downloadBook = async (client: any, b: number) => {
  const everett = new PatriotPropertiesAPI('everett');
  const pageCount = await everett.getBookPageCount(b);

  const promises = [];
  for (let p = 1; p <= pageCount; ++p) {
    promises.push(everett.getPropertyList({
      SearchBook: b,
      SearchPage: p,
    }).then(properties => {
      if (properties.length > 0) {
        const dataToSave = properties.map(p => ({patriotProperties: p}));
        client.db('dev').collection('patriot').insertMany(dataToSave);
        console.log(`Saved book ${b} page ${p}.`);
      }
    }));
  }
  return Promise.all(promises);
}

const runMe = async () => {

  const client = new mongo.MongoClient('mongodb://localhost:27020');

  await client.connect();
  await client.db('dev').command({ping: 1});
  console.log('Connected!');

  const downloadThenWait = async (wait: number, bStart: number, bEnd: number) => {
    await downloadBook(client, bStart);
    console.log(`Finished book ${bStart}.`);
    if (bStart < bEnd) {
      console.log(`Waiting ${wait/1000} seconds before starting next book...`);
      setTimeout(() => downloadThenWait(wait, bStart+1, bEnd), wait);
    } else {
      console.log('All done!');
    }
  }
  downloadThenWait(100, 1, 1000);
};

runMe();
