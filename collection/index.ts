import PatriotPropertiesAPI from "./sources/patriot-properties";
import mongo from "mongodb";
import pThrottle from "p-throttle";

const city = process.argv[2];

if (!city) {
  console.error("Please provide a valid city name as a command line argument.");
  process.exit(1);
}

// Be nice to the server and don't hammer it with requests
const throttle = pThrottle({
  limit: 2, // Maximum number of API requests per interval
  interval: 2000, // Interval in milliseconds
  onDelay: () => {
    console.log("Reached interval limit, call is delayed");
  },
});

const processPage = throttle(
  async (client, scraper, year_built, p, pageCount) => {
    try {
      const properties = await scraper.getPropertyList({
        SearchYearBuilt: year_built,
      });

      if (properties.length > 0) {
        const upsertOperations = properties.map((property) => ({
          updateOne: {
            filter: { _id: property.parcelId },
            update: { $set: { bookEntry: property } },
            upsert: true,
          },
        }));
        await client
          .db("dev")
          .collection(`patriot.${city}`)
          .bulkWrite(upsertOperations);
      }

      console.log(`Processed page ${p} of ${pageCount}`);
    } catch (error) {
      console.error(`Error processing page ${p} of ${pageCount}:`, error);
    }
  }
);

const downloadBook = async (client: any, year_built: number) => {
  const scraper = new PatriotPropertiesAPI(city);
  const pageCount = await scraper.getPageCount(year_built);

  console.log(`Processing ${pageCount} pages of properties.`);
  const promises = [];

  for (let p = 1; p <= pageCount; ++p) {
    promises.push(processPage(client, scraper, year_built, p, pageCount));
  }

  await Promise.all(promises);
};

const runMe = async () => {
  const client = new mongo.MongoClient("mongodb://localhost:27020", {
    useUnifiedTopology: true,
  });

  try {
    await client.connect();
    console.log("Connected to MongoDB!");

    await downloadBook(client, 0);
    console.log("Finished downloading data");

    console.log("All done!");
  } catch (error) {
    console.error("An error occurred:", error);
  } finally {
    await client.close();
    console.log("MongoDB connection closed.");
  }
};

runMe();
