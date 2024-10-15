import styled from "styled-components";
const Login = (props) => {
    return (
        <Container>
          <Nav>
            <a href="/">
            <img src="/images/Bulletin-writtenlarge.png" alt="" className="h-20 p-0 w-25" />
            </a>
            <div>
                <Join>Join now</Join>
                <SignIn>Sign In</SignIn>
            </div>
          </Nav>
          <Section>
            <Hero>
                <h1>'Connecting minds, creating futures.'</h1>
                <img src="/images/happy.png" alt="cover page"/>
            </Hero>
            <Form>
                <Google>
                    <img src="/images/google logo.svg" alt="gg" className="h-10"/>
                    Sign in with Google
                </Google>
            </Form>

          </Section>
        </Container>
    );
};

const Container = styled.div`
padding: 0px;
`;
        
const Nav = styled.nav`

max-width: 1128px;
margin: auto;
padding: 12px 0 16px;
display: flex;
align-items: center;
position: relative;
justify-content: space-between;
flex-wrap: nowrap;

& > a {
    width: 135px;
    height: 34px;
    @media (max-width: 768px) {
        padding: 0 5px;
    }
}
`;

const Join = styled.a`
font-size: 16px;
padding: 10px 12px;
text-decoration: none;
border-radius: 4px;
color: lightgray;
margin-right: 12px;

&:hover {
    background-color: rgba(0, 0, 0, 0.08);
    color: darkgray;
    text-decoration: none;
}
`;

const SignIn = styled.a`
box-shadow: inset 0 0 0 1px lightgoldenrodyellow;
color: lightgoldenrodyellow;
border-radius: 24px;
transition-duration: 167ms;
font-size: 16px;
line-height: 40px;
font-weight: 600;
padding: 10px 24px;
text-align: center;
background-color: rgba(0, 0, 0, 0);

&:hover {
    background-color: rgba(112, 181, 249, 0.15);
    color: yellow;
    text-decoration: none;
}


`;

const Section = styled.section`
display: flex;
align-content: start;
min-height: 700px;
padding-bottom: 138px;
padding-top: 40px;
padding: 60px 0;
position: relative;
flex-wrap: wrap;
width: 100%;
max-width: 1128px;
align-items: center;
margin: auto;
@media (max-width:768px) {
    margin: auto;
    min-height: 0px;
}

`;

const Hero = styled.div`
color: white;
width: 100%;
h1 {
    padding-bottom: 0;
    width: 55%;
    font-size: 56px;
    color: white;
    font-weight: 200;
    line-height: 70px;
    @media (max-width: 768px) {
        text-align: center;
        font-size: 20px;
        width: 100%;
        line-height: 2;
    }
}

img {
    
    width: 700px;
    height: 670px;
    position: absolute;
    bottom: -2px;
    right: -150px;
    border-radius: 50%;
    @media (max-width: 768px) {
        top: 230px;
        position: initial;
        width: initial;
        height: initial;
        border-radius: 50%;
    }
}


`;

const Form=styled.div`
margin-top: 100px;
width: 408px;
@media (max-width: 768px) {
    margin-top: 20px;

}
`;
const Google=styled.button`
color: black;
background-color: white;
display: flex;
justify-content: center;
align-items: center;
height: 56px;
width: 100%;
border-radius: 28px;
border-color: white;
box-shadow: inset 0 0 0 1px rgb(0 0 0 / 60%), inset 0 0 0 2px rgb(0 0 0 / 0%) inset 0 0 0 1px rgb(0 0 0 / 0%);
vertical-align: middle;
z-index: 0;
transition-duration: 167ms;
font-size: 20px;
color: rgba(0, 0, 0, 0.6);
&:hover {
    background-color: rgba(207, 207, 207, 0.25);
    color: rgba(0, 0, 0, 0.75);
}
`;



export default Login;