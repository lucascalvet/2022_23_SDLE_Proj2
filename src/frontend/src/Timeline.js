import React from "react";
import { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardHeader,
  CardContent,
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
} from "@mui/material/";
import { Person, QrCode2, QrCodeScanner } from "@mui/icons-material";
import QRCode from "react-qr-code";
import Html5QrcodePlugin from "./Html5QrcodePlugin";

export default function TwitterFeed() {
  const [posts, setPosts] = React.useState([]);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [QROpen, setQROpen] = React.useState(false);
  const [QRReadOpen, setQRReadOpen] = React.useState(false);
  const [pubKey, setPubKey] = React.useState(null);

  const fetchData = async () => {
    const API_ENDPOINT = "http://localhost:8000/timeline";
    const response = await fetch(API_ENDPOINT, {
      method: "GET",
      mode: "cors",
    });
    const json = await response.json();
    setPosts(json);
  };
  const fetchPubKey = async () => {
    const API_ENDPOINT = "http://localhost:8000/pubkey";
    const response = await fetch(API_ENDPOINT, {
      method: "GET",
      mode: "cors",
    });
    const json = await response.json();
    setPubKey(json["pubkey"]);
  };

  useEffect(() => {
    fetchData();
    fetchPubKey();
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
    // make a request to the API to post
    const API_ENDPOINT = "http://localhost:8000/";
    await fetch(API_ENDPOINT + "post", {
      method: "POST",
      mode: "cors",
      body: JSON.stringify({ text: tweetText }),
    });

    // fetch the updated list of posts and update the posts state variable
    const response = await fetch(API_ENDPOINT + "timeline", {
      method: "GET",
      mode: "cors",
    });
    const json = await response.json();
    setPosts(json);
  };

  const onNewScanResult = (decodedText, decodedResult) => {
    handleQRReadClose();
    //TODO: Do the follow with the key in decodedText
    console.log(decodedText);
    console.log(decodedResult);
  };

  return (
    <div
      style={{
        display: "flex",
        width: "100%",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center"
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
          <div style={{ height: "auto", margin: "0 auto", maxWidth: 200, width: "100%" }}>
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
        <DialogTitle id="qr-read-dialog-title">{"Scan a public key"}</DialogTitle>
        <DialogContent
          sx={{
            display: "flex",
            alignItems: "center",
            flexDirection: "column",
          }}
        >
          <Box sx={{ width: "400px", height: "400px" }} >
            <Html5QrcodePlugin
              fps={10}
              qrbox={{ width: 250, height: 250 }}
              disableFlip={false}
              qrCodeSuccessCallback={onNewScanResult} />

          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleQRReadClose} autoFocus>
            Close
          </Button>
        </DialogActions>
      </Dialog>
      <Card style={{ margin: "auto", width: "90%" }}>
        <CardHeader
          avatar={
            <Avatar aria-label="Twitter">
              <Person />
            </Avatar>
          }
          action={
            <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
              <TextField
                id="twitter-search"
                label="Search"
                type="search"
                margin="normal"
                value={searchQuery}
                onChange={handleSearchChange}
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
        <Box sx={{ display: "flex", alignItems: "center", flexDirection: "column" }}>
          <IconButton onClick={handleQRClickOpen}>
            <QrCode2 sx={{ fontSize: "80px" }} />
          </IconButton>
          <IconButton onClick={handleQRReadClickOpen}>
            <QrCodeScanner sx={{ fontSize: "80px" }} />
          </IconButton>
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
            />
            <Button
              style={{ height: "50px", borderRadius: "5px" }}
              variant="contained"
              color="primary"
              onClick={handleTweetSubmit}
            >
              Post
            </Button>
          </div>
        </Box>
        <CardContent style={{ marginLeft: "25px", marginRight: "25px" }}>
          <Grid container direction="column" spacing={2}>
            {posts.map((post) => (
              <Grid item key={post.id}>
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
    </div>
  );
}
