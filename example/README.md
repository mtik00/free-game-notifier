# Docker Example

The files and folders in this directory are set up to be copied to your docker
server and ran with `docker-compose up`.

## Setup

1.  Copy this folder to your docker server.
1.  Make sure you are inside the folder
1.  Create a folder for your application cache folder:
    ```
    mkdir -p app_cache && chmod 777 app_cache
    ```
1.  Grab the latest Steam RSS feed to test with
    ```
    curl -o feed.xml https://steamcommunity.com/groups/freegamesfinders/rss/
    ```
1.  The folder structure should now look like this:
    ```
    .
    ├── README.md
    ├── app_cache
    ├── docker-compose.yml
    └── settings.yml
    ```
1.  Modify `settings.yml` as needed
1.  Test the application with:
    ```
    docker-compose up
    ```

Once you verify everything is working as intended, modify `settings.yml` to your
liking.  The two main things to change are `feeds.steam.url` (you'll want to use
the actual RSS feed) and `notifiers.slack.url` for your actual Slack webhook.
