import React from "react";
import { useEffect, useState } from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  Avatar,
  Typography,
  IconButton,
  Grid,
  TextField,
} from "@mui/material/";
import { Person, Add } from "@mui/icons-material";

 /* const useStyles = makeStyles((theme) => ({
   card: {
     maxWidth: 600,
     margin: "auto",
     marginTop: theme.spacing(5),
   },
   cardContent: {
     padding: theme.spacing(2),
   },
   cardHeader: {
     padding: theme.spacing(1, 2),
   },
   textField: {
     marginLeft: theme.spacing(1),
     marginRight: theme.spacing(1),
     width: 200,
   },
   followButton: {
     marginLeft: "auto",
   },
   avatar: {
     backgroundColor: theme.palette.primary.main,
   },
 })); */

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

  return (
    <Card style = {{margin: "auto", marginTop: "5px" }}>
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
        {/* <div>
          {posts.map((post) => (
            <p>
              {post.text}
              {" - "}
              {post.author_alias}
              {" ("}
              {new Date(post.timestamp * 1000).toLocaleString()}
              {")"}
            </p>
          ))}
        </div> */}
      </CardContent>
    </Card>
  );
};
