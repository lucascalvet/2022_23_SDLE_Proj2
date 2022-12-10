import React from "react";
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

// const useStyles = makeStyles((theme) => ({
//   card: {
//     maxWidth: 600,
//     margin: "auto",
//     marginTop: theme.spacing(5),
//   },
//   cardContent: {
//     padding: theme.spacing(2),
//   },
//   cardHeader: {
//     padding: theme.spacing(1, 2),
//   },
//   textField: {
//     marginLeft: theme.spacing(1),
//     marginRight: theme.spacing(1),
//     width: 200,
//   },
//   followButton: {
//     marginLeft: "auto",
//   },
//   avatar: {
//     backgroundColor: theme.palette.primary.main,
//   },
// }));

const TwitterFeed = () => {
  const [tweets, setTweets] = React.useState([]);
  const [searchQuery, setSearchQuery] = React.useState("");

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
    <Card >
      <CardHeader
        avatar={
          <Avatar aria-label="Twitter" >
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
      <CardContent>
        <Grid container direction="column" spacing={2}>
          {tweets.map((tweet) => (
            <Grid item key={tweet.id}>
              <Grid container alignItems="center" spacing={1}>
                <Grid item>
                  <Avatar alt={tweet.username} src={tweet.avatar} />
                </Grid>
                <Grid item>
                  <Typography variant="body1">{tweet.username}</Typography>
                </Grid>
                <Grid item xs>
                  <Typography variant="body2" color="textSecondary">
                    {tweet.text}
                  </Typography>
                </Grid>
                <Grid item>
                  {tweet.isFollowing ? (
                    <IconButton onClick={() => handleUnfollow(tweet.id)}>
                      <Person />
                    </IconButton>
                  ) : (
                    <IconButton onClick={() => handleFollow(tweet.id)}>
                      <Add />
                    </IconButton>
                  )}
                </Grid>
              </Grid>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default TwitterFeed;
