import './terms.css'

export default function Terms(){
  return (
    <div className="terms">
      {/* gradient cap to match your style */}
      <div className="terms-hero">
        <div className="container">
          <div className="terms-brand">
            <img src="/assets/logo-titan.svg" alt="TITAN" />
            <span>COLLECTIBLES</span>
          </div>
        </div>
      </div>

      <div className="container">
        <article className="terms-card">
          <h1>Terms of Use</h1>
          <p className="terms-meta">Effective Date: July 31, 2025</p>

          <p>
            Welcome to Titan. These Terms of Use (“Terms”) govern your access to and use of the Titan website, digital products,
            and services (collectively, the “Services”), operated by Titan Sports and Collectibles Inc. By accessing or using the
            Services, you agree to be bound by these Terms and our <a href="/privacy">Privacy Policy</a>. If you do not agree,
            please do not use Titan.
          </p>

          <h3>1. Overview</h3>
          <p>
            Titan is a digital platform that offers sports cards, athlete-focused collectibles, and related content to fans and
            collectors worldwide. We aim to deliver a fair, transparent, and secure user experience for everyone who visits or
            interacts with our Services.
          </p>

          <h3>2. Eligibility</h3>
          <p>
            To use Titan, you must be at least 13 years old. If you are under 18, you may only use the Services under the
            supervision of a parent or legal guardian who agrees to these Terms on your behalf. By using Titan, you confirm that
            you meet these requirements.
          </p>

          <h3>3. User Accounts</h3>
          <p>You may need to create an account to access certain features. You agree to:</p>
          <ul>
            <li>Provide accurate, current information when registering.</li>
            <li>Keep your login credentials secure.</li>
            <li>Notify us immediately at support@titansportshq.com of any unauthorized use.</li>
          </ul>
          <p>You are responsible for all activity under your account.</p>

          <h3>4. Acceptable Use</h3>
          <p>By using the Services, you agree not to:</p>
          <ul>
            <li>Violate any laws, regulations, or third-party rights.</li>
            <li>Post or upload any defamatory, abusive, obscene, or infringing content.</li>
            <li>Interfere with or disrupt the integrity of our platform, systems, or security.</li>
            <li>Use bots, scrapers, or other automated tools without our prior written permission.</li>
          </ul>
          <p>We reserve the right to suspend or terminate your account if you violate these Terms.</p>

          <h3>5. Intellectual Property</h3>
          <p>
            All content on Titan—including images, cards, text, logos, software, and design—is the intellectual property of Titan
            Sports and Collectibles Inc. or its partners and is protected by international copyright, trademark, and other laws.
            You may not copy, reproduce, modify, distribute, or create derivative works from any part of the Services without our
            explicit written permission.
          </p>

          <h3>6. User Submissions</h3>
          <p>
            If you submit content to Titan—such as reviews, comments, or uploaded media—you grant Titan Sports and Collectibles
            Inc. a non-exclusive, worldwide, royalty-free license to use, display, reproduce, modify, and distribute that content
            as part of operating and promoting the Services. You retain ownership of your submitted content and remain responsible
            for its legality and accuracy.
          </p>

          <h3>7. Purchases and Payment</h3>
          <p>
            Titan offers both physical and digital collectible products. By placing an order, you agree to:
          </p>
          <ul>
            <li>Provide accurate payment and shipping information.</li>
            <li>Pay all applicable fees, taxes, and shipping costs.</li>
            <li>Understand that all sales are final unless otherwise specified in our refund policy.</li>
            <li>
              Shipping Responsibility: Customers are responsible for all shipping costs. Titan Sports and Collectibles Inc. is not
              liable for lost, stolen, or delayed shipments once orders have been handed off to the carrier.
            </li>
          </ul>
          <p>
            Prices and availability are subject to change without notice. Titan Sports and Collectibles Inc. reserves the right to
            cancel orders due to errors, fraud, or stock issues.
          </p>

          <h3>8. Disclaimers</h3>
          <p>The Services are provided “as is” and “as available.” We do not guarantee that the platform will be error-free or uninterrupted. We disclaim all warranties, express or implied, including merchantability, fitness for a particular purpose, and non-infringement.</p>
          <p>We are not responsible for:</p>
          <ul>
            <li>User-generated content.</li>
            <li>Delays or delivery failures beyond our control.</li>
            <li>Loss of data, revenue, or business due to your use of the Services.</li>
          </ul>

          <h3>9. Limitation of Liability</h3>
          <p>
            To the fullest extent permitted by law, Titan Sports and Collectibles Inc. and its affiliates will not be liable for any
            indirect, incidental, consequential, or punitive damages arising from your use or inability to use the Services. Our
            total liability to you for any claim will not exceed the amount you paid (if any) to use the Services in the past 12 months.
          </p>

          <h3>10. Suspension and Termination</h3>
          <p>We may suspend or terminate your access to the Services at any time, with or without notice, if:</p>
          <ul>
            <li>You violate these Terms.</li>
            <li>Your activity poses a risk to the platform or other users.</li>
            <li>We are required to do so by law or legal authority.</li>
          </ul>
          <p>Upon termination, your rights to use the Services will immediately cease.</p>

          <h3>11. Governing Law</h3>
          <p>
            These Terms are governed by and interpreted under the laws of Canada, without regard to conflict-of-law principles. Any
            disputes shall be resolved exclusively in the courts of Ontario, Canada.
          </p>

          <h3>12. Changes to These Terms</h3>
          <p>
            We may revise these Terms from time to time. If changes are significant, we will notify you via the website or email.
            Your continued use of the Services after changes take effect constitutes your acceptance of the revised Terms.
          </p>
        </article>
      </div>
    </div>
  )
}
