import React from "react";
import { useEffect, useState } from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  Avatar,
  Typography,
  IconButton,
  Button,
  Grid,
  TextField,
} from "@mui/material/";
import { Person, Add } from "@mui/icons-material";

export default function TwitterFeed() {
  const [posts, setPosts] = React.useState([]);
  const [searchQuery, setSearchQuery] = React.useState("");

  useEffect(() => {
    const fetchData = async () => {
      const API_ENDPOINT = "http://localhost:8000/timeline";
      const response = await fetch(API_ENDPOINT, {
        method: 'GET',
        mode: 'cors',
    });
      const json = await response.json();
      setPosts(json);
    };
    fetchData();
  }, []);

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleFollow = (tweetId) => {
    // Code to follow a user goes here
  };

  const handleUnfollow = (tweetId) => {
    // Code to unfollow a user goes here
  };

  const handleTweetChange = (event) => {
    setTweetText(event.target.value); // update the tweet text state variable
  };  

  const handleTweetSubmit = async () => {
    // make a request to the API to post the tweet
    const API_ENDPOINT = "http://localhost:8000/post";
    await fetch(API_ENDPOINT, {
      method: 'POST',
      mode: 'cors',
      body: JSON.stringify({ text: tweetText }),
    });

    // fetch the updated list of tweets and update the posts state variable
    const response = await fetch(API_ENDPOINT, {
      method: 'GET',
      mode: 'cors',
    });
    const json = await response.json();
    setPosts(json);
  }

  return (
    <div style = {{display: "flex", marginTop: "5px", width: "100%", flexDirection: "column"}}>
          <Card style = {{margin: "auto", marginTop: "5px", width: "100%"}}>
      <CardHeader 
        avatar={
          <Avatar aria-label="Twitter">
            <Person />
          </Avatar>
        }
        action={
          <TextField  
            id="twitter-search"
            label="Search"
            type="search"
            margin="normal"
            value={searchQuery}
            onChange={handleSearchChange}
          />
        }
        title="Twitter Feed"
        subheader="Latest tweets from your followers"
      />
      <CardContent style = {{padding: "5px"}}>
        <Grid container direction="column" spacing={2}>
        {posts.map((post) => (
            <Grid item key={1}>
              <Grid container alignItems="center" spacing={1}>
                <Grid item>
                  <Typography variant="body1">{post.author_alias}</Typography>
                </Grid>
                <Grid item xs>
                  <Typography variant="body2" color="textSecondary">
                    {post.text}
                  </Typography>
                </Grid>
                <Grid item>
                  <IconButton onClick={() => handleUnfollow(1)}>
                    <Person />
                  </IconButton>
                </Grid>
              </Grid>
            </Grid>
            ))}
        </Grid>
      </CardContent>
    </Card>
    <div style={{marginTop: "50px" , display: "flex", alignItems: "center", justifyContent: "center", width: "100%"}}>
      <TextField id="input-field" label="Enter a new post" style={{width: "50%",marginRight: "5px", borderRadius: "0px"}} />
      <Button style = {{height: "50px", borderRadius: "0px"}} variant="contained" color="primary" onClick={handleTweetSubmit}>
        Post
      </Button>
    </div>
    </div>

  );
};
