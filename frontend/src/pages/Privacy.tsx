import './terms.css' // reuse the same legal styles

export default function Privacy(){
  return (
    <div className="terms">{/* reuse .terms wrapper styles */}


      <div className="container">
        <article className="terms-card">
          <h1>Privacy Policy</h1>
          <p className="terms-meta">Effective Date: July 31, 2025</p>

          <p>
            Titan Sports and Collectibles Inc. (“Titan”, “we”, “our”, or “us”) is committed to protecting your privacy.
            This Privacy Policy explains how we collect, use, disclose, and protect your personal information when you
            visit our website, use our services, or interact with us. By using Titan’s services, you agree to the terms
            of this Privacy Policy.
          </p>

          <h3>1. Information We Collect</h3>
          <p>We collect the following types of information:</p>
          <p><strong>a. Information You Provide</strong></p>
          <ul>
            <li><strong>Account Information:</strong> When you sign up, we collect your name, email, phone number, shipping address, and password.</li>
            <li><strong>Payment Information:</strong> When you make a purchase, we collect payment data (e.g., card details, billing address) via our third-party payment processor (we do not store full card details).</li>
            <li><strong>Communications:</strong> If you contact us or participate in promotions, we collect any information you provide, such as inquiries, feedback, or survey responses.</li>
          </ul>
          <p><strong>b. Information Collected Automatically</strong></p>
          <ul>
            <li><strong>Device and Usage Information:</strong> We collect data such as IP address, browser type, pages visited, referring/exit pages, and timestamps.</li>
            <li><strong>Cookies and Tracking Technologies:</strong> We use cookies and similar tools to enhance your browsing experience and understand usage patterns.</li>
          </ul>
          <p>You can control cookies through your browser settings. Disabling cookies may affect site functionality.</p>

          <h3>2. How We Use Your Information</h3>
          <p>We use your personal information to:</p>
          <ul>
            <li>Process orders, payments, and deliveries.</li>
            <li>Provide customer support and respond to inquiries.</li>
            <li>Send transactional emails (e.g., order confirmations).</li>
            <li>Send marketing communications (with your consent).</li>
            <li>Improve our services, features, and website performance.</li>
            <li>Detect and prevent fraud or misuse of our platform.</li>
            <li>Comply with legal obligations.</li>
          </ul>

          <h3>3. Sharing Your Information</h3>
          <p>We do not sell your personal information. We may share it with:</p>
          <ul>
            <li><strong>Service Providers:</strong> Trusted third parties that help us operate the site (e.g., payment processors, email services, hosting providers).</li>
            <li><strong>Legal Authorities:</strong> When required to comply with the law, respond to legal requests, or protect our rights.</li>
            <li><strong>Business Transfers:</strong> If Titan is involved in a merger, acquisition, or sale of assets, your data may be transferred as part of that transaction.</li>
          </ul>
          <p>All third parties are obligated to protect your information and use it only for the intended purpose.</p>

          <h3>4. Data Retention</h3>
          <p>We retain your personal data for as long as necessary to:</p>
          <ul>
            <li>Provide the services you requested.</li>
            <li>Comply with our legal obligations.</li>
            <li>Resolve disputes and enforce agreements.</li>
          </ul>
          <p>You may request deletion of your account and personal data at any time by contacting us at <a href="mailto:support@titansports.ca">support@titansports.ca</a>.</p>

          <h3>5. Your Rights and Choices</h3>
          <p>
            Depending on your location, you may have rights under laws such as the General Data Protection Regulation (GDPR)
            or the Personal Information Protection Act (PIPA) in Canada. These may include:
          </p>
          <ul>
            <li>The right to access, correct, or delete your personal data.</li>
            <li>The right to object to processing or withdraw consent.</li>
            <li>The right to data portability.</li>
            <li>The right to file a complaint with a supervisory authority.</li>
          </ul>
          <p>To exercise your rights, email us at <a href="mailto:support@titansportshq.com">support@titansportshq.com</a>.</p>

          <h3>6. Marketing Communications</h3>
          <p>
            If you opt in, we may send you updates, offers, and promotional content. You can unsubscribe at any time by
            clicking the “unsubscribe” link in our emails or updating your preferences in your account settings.
          </p>

          <h3>7. Data Security</h3>
          <p>
            We implement industry-standard technical and organizational measures to protect your data from unauthorized access,
            use, or disclosure. However, no method of transmission over the internet is 100% secure. You use our Services at
            your own risk.
          </p>

          <h3>8. Children’s Privacy</h3>
          <p>
            Titan is not intended for use by children under the age of 13. We do not knowingly collect personal data from
            children. If we learn we’ve collected such data, we will delete it immediately.
          </p>

          <h3>9. Changes to This Policy</h3>
          <p>
            We may update this Privacy Policy occasionally. If we make material changes, we will notify you by posting a
            prominent notice on our website or emailing you directly. Continued use of our Services after updates means you
            accept the new terms.
          </p>
        </article>
      </div>
    </div>
  )
}
