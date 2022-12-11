import React from "react";
import { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardHeader,
  CardContent,
  Divider,
  Avatar,
  Typography,
  IconButton,
  Button,
  Grid,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  Paper,
  List,
  ListItem,
  ListItemText,
} from "@mui/material/";
import { Person, QrCode2, QrCodeScanner } from "@mui/icons-material";
import QRCode from "react-qr-code";
import Html5QrcodePlugin from "./Html5QrcodePlugin";

export default function TwitterFeed() {
  const [posts, setPosts] = React.useState([]);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [alias, setAlias] = React.useState("");
  const [QROpen, setQROpen] = React.useState(false);
  const [QRReadOpen, setQRReadOpen] = React.useState(false);
  const [pubKey, setPubKey] = React.useState(null);
  const [subscriptions, setSubscriptions] = React.useState([]);
  const [subscribed, setSubscribed] = React.useState([]);
  const [postText, setPostText] = React.useState([]);

  const API_ENDPOINT = "http://localhost:8000/";

  const fetchData = async () => {
    const response = await fetch(API_ENDPOINT + "timeline", {
      method: "GET",
      mode: "cors",
    });
    const json = await response.json();
    setPosts(json);
  };
  const fetchPubKey = async () => {
    const response = await fetch(API_ENDPOINT + "pubkey", {
      method: "GET",
      mode: "cors",
    });
    const json = await response.json();
    setPubKey(json["pubkey"]);
  };
  const fetchSubscriptions = async () => {
    const response = await fetch(API_ENDPOINT + "subscriptions", {
      method: "GET",
      mode: "cors",
    });
    const json = await response.json();
    setSubscriptions(json);
  };
  const fetchSubscribed = async () => {
    const response = await fetch(API_ENDPOINT + "subscribed", {
      method: "GET",
      mode: "cors",
    });
    const json = await response.json();
    setSubscribed(json);
  };
  const fetchFollow = async (pubkey, alias) => {
    const response = await fetch(
      `${API_ENDPOINT}subscribe?pubkey=${pubkey}&alias=${alias}`,
      {
        method: "GET",
        mode: "cors",
      }
    );
    const json = await response.json();
    //setSubscribed(json);
  };
  const fetchUnfollow = async (pubkey) => {
    const response = await fetch(
      `${API_ENDPOINT}unsubscribe?pubkey=${pubkey}`,
      {
        method: "GET",
        mode: "cors",
      }
    );
    const json = await response.json();
    //setSubscribed(json);
  };

  useEffect(() => {
    fetchData();
    fetchPubKey();
    fetchSubscriptions();
    fetchSubscribed();

    const interval = setInterval(() => {
      fetchSubscriptions();
      fetchSubscribed();
      fetchData();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleQRClickOpen = () => {
    setQROpen(true);
  };

  const handleQRClose = () => {
    setQROpen(false);
  };

  const handleQRReadClickOpen = () => {
    setQRReadOpen(true);
  };

  const handleQRReadClose = () => {
    setQRReadOpen(false);
  };

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleFollow = () => {
    // Code to follow a user goes here
    fetchFollow(searchQuery, alias);
    fetchSubscribed();
  };

  const handleUnfollow = (pubkey) => {
    // Code to unfollow a user goes here
    fetchUnfollow(pubkey);
  };

  const handleAliasChange = (event) => {
    setAlias(event.target.value); // update the post text state variable
  };

  const handlePostTextChange = (event) => {
    setPostText(event.target.value); // update the post text state variable
  };

  const handlePostSubmit = async () => {
    // make a request to the API to post
    await fetch(API_ENDPOINT + "post", {
      method: "POST",
      mode: "cors",
      body: postText,
    });
    setPostText("");

    fetchData();
  };

  const onNewScanResult = (decodedText, decodedResult) => {
    handleQRReadClose();
    //TODO: Do the follow with the key in decodedText
    console.log(decodedText);
    console.log(decodedResult);
  };

  /* const unixTimestampToString = (timestamp) => {
    let date = new Date(timestamp * 1000);

    let year = date.getFullYear();
    let month = String(date.getMonth() + 1).padStart(2, "0");
    let day = String(date.getDate()).padStart(2, "0");
    let hours = String(date.getHours()).padStart(2, "0"); 
    let minutes = String(date.getMinutes()).padStart(2, "0"); 
    let seconds = String(date.getSeconds()).padStart(2, "0"); 

    let dateString = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;

    return dateString;
  }; */

  return (
    <div
      style={{
        display: "flex",
        width: "100%",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Dialog
        open={QROpen}
        onClose={handleQRClose}
        aria-labelledby="qr-dialog-title"
        aria-describedby="qr-dialog-description"
      >
        <DialogTitle id="qr-dialog-title">{"Your public key"}</DialogTitle>
        <DialogContent
          sx={{
            display: "flex",
            alignItems: "center",
            flexDirection: "column",
          }}
        >
          <div
            style={{
              height: "auto",
              margin: "0 auto",
              maxWidth: 200,
              width: "100%",
            }}
          >
            <QRCode
              size={256}
              style={{ height: "auto", maxWidth: "100%", width: "100%" }}
              value={pubKey}
              viewBox={`0 0 256 256`}
            />
          </div>
          <DialogContentText
            id="qr-dialog-description"
            sx={{ fontSize: "13px", marginTop: "15px" }}
          >
            {pubKey}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleQRClose} autoFocus>
            Close
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={QRReadOpen}
        onClose={handleQRReadClose}
        aria-labelledby="qr-read-dialog-title"
        aria-describedby="qr-read-dialog-description"
      >
        <DialogTitle id="qr-read-dialog-title">
          {"Scan a public key"}
        </DialogTitle>
        <DialogContent
          sx={{
            display: "flex",
            alignItems: "center",
            flexDirection: "column",
          }}
        >
          <Box sx={{ width: "400px", height: "400px" }}>
            <Html5QrcodePlugin
              fps={10}
              qrbox={{ width: 250, height: 250 }}
              disableFlip={false}
              qrCodeSuccessCallback={onNewScanResult}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleQRReadClose} autoFocus>
            Close
          </Button>
        </DialogActions>
      </Dialog>
      <Card style={{ margin: "auto", width: "95%" }}>
        <CardHeader
          avatar={
            <Avatar aria-label="Twitter">
              <Person />
            </Avatar>
          }
          action={
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <TextField
                id="twitter-search"
                label="pubkey"
                type="search"
                inputProps={{ style: { fontSize: 12, width: "475px" } }}
                InputLabelProps={{ style: { fontSize: 12 } }}
                margin="normal"
                sx={{
                  marginRight: "10px",
                }}
                value={searchQuery}
                onChange={handleSearchChange}
              />
              <TextField
                id="alias"
                label="alias"
                type="search"
                inputProps={{ style: { fontSize: 12, width: "100px" } }}
                InputLabelProps={{ style: { fontSize: 12 } }}
                margin="normal"
                value={alias}
                onChange={handleAliasChange}
              />
              <Button
                style={{ borderRadius: "5px", marginLeft: "10px" }}
                variant="contained"
                color="primary"
                onClick={handleFollow}
              >
                Follow
              </Button>
            </Box>
          }
        />
        <Grid container spacing={2} sx={{ width: "100%", marginLeft: "-10px" }}>
          <Grid item xs={12} md={5}>
            <Paper
              sx={{
                maxHeight: 300,
                height: 300,
                width: "100%",
                overflow: "auto",
              }}
            >
              <List>
                <ListItem key="title">
                  <ListItemText
                    primary={"Followers"}
                    primaryTypographyProps={{
                      fontSize: 20,
                      fontWeight: "bold",
                    }}
                  />
                </ListItem>
                <Divider key="title-divider" />
                {subscribed.map((user, index) => (
                  <React.Fragment>
                    <ListItem key={index}>
                      <ListItemText
                        primary={user.alias}
                        secondary={user.pubkey}
                        secondaryTypographyProps={{ fontSize: 10 }}
                      />
                    </ListItem>
                    <Divider key={index + "-divider"} />
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          </Grid>
          <Grid item xs={12} md={1}>
            <IconButton onClick={handleQRClickOpen}>
              <QrCode2 sx={{ fontSize: "80px" }} />
            </IconButton>
          </Grid>
          <Grid item xs={12} md={1}>
            <IconButton onClick={handleQRReadClickOpen}>
              <QrCodeScanner sx={{ fontSize: "80px" }} />
            </IconButton>
          </Grid>
          <Grid item xs={12} md={5}>
            <Paper
              sx={{
                maxHeight: 300,
                height: 300,
                width: "100%",
                overflow: "auto",
              }}
            >
              <List>
                <ListItem key="title">
                  <ListItemText
                    primary={"Following"}
                    primaryTypographyProps={{
                      fontSize: 20,
                      fontWeight: "bold",
                    }}
                  />
                </ListItem>
                <Divider />
                {subscriptions.map((user, index) => (
                  <React.Fragment>
                    <ListItem key={index}>
                      <ListItemText
                        primary={user.alias}
                        secondary={user.pubkey}
                        secondaryTypographyProps={{ fontSize: 10 }}
                      />
                      <Button
                        style={{ borderRadius: "5px" }}
                        variant="contained"
                        color="primary"
                        onClick={() => handleUnfollow(user.pubkey)}
                      >
                        Unfollow
                      </Button>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            flexDirection: "column",
          }}
        >
          <div
            style={{
              marginTop: "25px",
              marginBottom: "25px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "100%",
            }}
          >
            <TextField
              id="input-field"
              label="Enter a new post"
              style={{ width: "50%", marginRight: "10px" }}
              value={postText}
              onChange={handlePostTextChange}
            />
            <Button
              style={{ height: "50px", borderRadius: "5px" }}
              variant="contained"
              color="primary"
              onClick={handlePostSubmit}
            >
              Post
            </Button>
          </div>
        </Box>
        <CardContent style={{ marginLeft: "25px", marginRight: "25px" }}>
          <Grid container direction="column" spacing={2}>
            {posts.map((post, index) => (
              <Grid item key={index}>
                <Grid container alignItems="center" spacing={1}>
                  <Grid item>
                    <Typography variant="body1">{post.author_alias}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      {post.formatted_date}
                    </Typography>
                  </Grid>
                  <Grid item xs>
                    <Typography variant="body2" color="textSecondary">
                      {post.text}
                    </Typography>
                  </Grid>
                  <Grid item>
                    <IconButton onClick={() => handleUnfollow(post.author)}>
                      <Person />
                    </IconButton>
                  </Grid>
                </Grid>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </div>
  );
}
